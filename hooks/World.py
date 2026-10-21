# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from typing import Any
from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState, Item

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
from ..Data import game_table, item_table, location_table, region_table

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value, format_state_prog_items_key, ProgItemsCat, remove_specific_item

# calling logging.info("message") anywhere below in this file will output the message to both console and log file
import logging

########################################################################################
## Order of method calls when the world generates:
##    1. create_regions - Creates regions and locations
##    2. create_items - Creates the item pool
##    3. set_rules - Creates rules for accessing regions and locations
##    4. generate_basic - Runs any post item pool options, like place item/category
##    5. pre_fill - Creates the victory location
##
## The create_item method is used by plando and start_inventory settings to create an item from an item name.
## The fill_slot_data method will be used to send data to the Manual client for later use, like deathlink.
########################################################################################

abilityListTrue: list[str] = [
        "Beam", "Beetle", "Bomb", "Cleaning", "Cook", "Cutter", "ESP", "Fighter", "Fire", "Hammer", "Ice", "Ninja", "Parasol", "Plasma", 
        "Stone", "Suplex", "Sword", "Water", "Whip", "Wing", "Yo-Yo", "Artist", "Spider", "Staff",
        "Bandana Waddle Dee", "Rick & Kine & Coo", "Marx", "Gooey", "Adeleine & Ribbon", "Dark Meta Knight", "Daroach", "Magolor", "Taranza", "Susie", 
        "Crash", "Mike", "Festival"]

# Use this function to change the valid filler items to be created to replace item links or starting items.
# Default value is the `filler_item_name` from game.json
def hook_get_filler_item_name(world: World, multiworld: MultiWorld, player: int) -> str | bool:
    filler_item_names = world.options.filler_item_pool.value
    return world.random.choice(filler_item_names)

def before_generate_early(world: World, multiworld: MultiWorld, player: int) -> None:
    """
    This is the earliest hook called during generation, before anything else is done.
    Use it to check or modify incompatible options, or to set up variables for later use.
    """
    pass

# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to remove locations from the world
    locationNamesToRemove: list[str] = [] # List of location names

    # Add your code here to calculate which locations to remove

    for region in multiworld.regions:
        if region.player == player:
            for location in list(region.locations):
                if location.name in locationNamesToRemove:
                    region.locations.remove(location)

# This hook allows you to access the item names & counts before the items are created. Use this to increase/decrease the amount of a specific item in the pool
# Valid item_config key/values:
# {"Item Name": 5} <- This will create qty 5 items using all the default settings
# {"Item Name": {"useful": 7}} <- This will create qty 7 items and force them to be classified as useful
# {"Item Name": {"progression": 2, "useful": 1}} <- This will create 3 items, with 2 classified as progression and 1 as useful
# {"Item Name": {0b0110: 5}} <- If you know the special flag for the item classes, you can also define non-standard options. This setup
#       will create 5 items that are the "useful trap" class
# {"Item Name": {ItemClassification.useful: 5}} <- You can also use the classification directly
def before_create_items_all(item_config: dict[str, int|dict], world: World, multiworld: MultiWorld, player: int) -> dict[str, int|dict]:
    item_config["Remove First Ally"] = world.options.trap_first_ally.value
    item_config["Remove Last Ally"] = world.options.trap_last_ally.value
    item_config["Remove Any Ally"] = world.options.trap_any_ally.value
    item_config["Remove All Allies"] = world.options.trap_all_allies.value
    item_config["Remove Copy Ability"] = world.options.trap_copy_ability.value
    item_config["No Jumps"] = world.options.trap_no_jumps.value
    item_config["Sleep"] = world.options.trap_sleep.value
    item_config["Flip Controller"] = world.options.trap_flip_controller.value
    return item_config

# The item pool before starting items are processed, in case you want to see the raw item pool at that stage
def before_create_items_starting(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    from random import shuffle
    abilityList: list[str] = ["Beam", "Beetle", "Bomb", "Cleaning", "Cook", "Cutter", "ESP", "Fighter", "Fire", "Hammer", "Ice", "Ninja", "Parasol", "Plasma", "Stone", "Suplex", "Sword", "Water", "Whip", "Wing", "Yo-Yo", "Artist", "Spider", "Staff"]
    dreamFriendList: list[str] = ["Bandana Waddle Dee", "Rick & Kine & Coo", "Marx", "Gooey", "Adeleine & Ribbon", "Dark Meta Knight", "Daroach", "Magolor", "Taranza", "Susie"]
    nonAllyAbilities: list[str] = ["Crash", "Mike", "Festival"]
    allyList: list[str] = []
    for a in abilityList:
        allyList.append(a)
    for d in dreamFriendList:
        allyList.append(d)
    if world.options.unify_dedede_metaknight == False:
        allyList.append("King Dedede")
        allyList.append("Meta Knight")
        dreamFriendList.append("King Dedede")
        dreamFriendList.append("Meta Knight")
        abilityListTrue.append("Meta Knight")
        abilityListTrue.append("King Dedede")
    if world.options.unify_magesisters == False or world.options.enable_heroes_in_another_dimension.value == False:
        if world.options.unlock_allies_with_hearts.value == False or world.options.last_heart_level_is_magesisters.value == False:
            allyList.append("The Three Mage-Sisters")
            dreamFriendList.append("The Three Mage-Sisters")
            abilityListTrue.append("The Three Mage-Sisters")
    shuffle(allyList)
    startAllyList: list[str] = allyList.copy()
    del startAllyList[world.options.starting_ally_count:]
    # Add allies to starting pool
    for a in startAllyList:
        item = next(i for i in item_pool if i.name == a)
        # print(item)
        remove_specific_item(item_pool, item)
        world.push_precollected(world.create_item(a))
        abilityListTrue.remove(a)
    # Add duplicate abilities
    for a in nonAllyAbilities:
        abilityList.append(a)
    # Only add dupes if friend heart unlocking is disabled
    if world.options.unlock_allies_with_hearts.value == False:
        for i in range(world.options.dupe_ability_count):
            for a in abilityList:
                item_pool.append(world.create_item(a))
        for i in range(world.options.dupe_dream_friend_count):
            for d in dreamFriendList:
                item_pool.append(world.create_item(d))
    else:
        shuffle(abilityListTrue)
        # Add Mage-Sisters after shuffle if they're supposed to be last
        if world.options.last_heart_level_is_magesisters.value == True:
            abilityListTrue.append("The Three Mage-Sisters")

    stageList: list[str] = [
            "Green Gardens", "Donut Dome", "Honey Hill", "Fruity Forest", "Clash at Castle Dedede",
            "Friendly Field","Reef Resort","Echo's Edge","Nature's Navel","Sacred Square",
            "Gatehouse Road","Eastern Wall","Longview Corridor","Western Outer Wall","Inner Sanctum","Heavenly Hall",
            "Planet Earthfall","Planet Misteen","Planet Caverna","Planet Frostak","Planet Towara","Star Lavadom","Jambandra Base", "Extra Planet Delta"
        ]
    exStages: list[str] = [
            "Extra Eclair","Inside Islands","Duplex Dream","Sector A","Sector B","Sector C",
            "Extra Planet Alpha","Extra Planet Beta","Extra Planet Gamma"
        ]
    moonStages: list[str] = [
            "Falluna Moon", "Mareen Moon","Grott Moon","Blizzno Moon","Gabbel Moon","Sizzlai Moon","The Divine Terminus"
        ]
    hiadStages: list[str] = [
            "Dimension I","Dimension II","Dimension III","Dimension IV"
        ]
    if world.options.unify_planets_and_moons.value == False:
        for m in moonStages:
            stageList.append(m)
    if world.options.unify_ex_stages.value == False:
        for ex in exStages:
            stageList.append(ex)
    if world.options.hiad_gating_methods.value == 2:
        for d in hiadStages:
            item_pool.append(world.create_item(d))
            stageList.append(d)
    shuffle(stageList)
    startStageList: list[str] = stageList.copy()
    del startStageList[world.options.starting_stage_count:]
    # Add shuffled stages to starting pool
    for s in startStageList:
        item = next(i for i in item_pool if i.name == s)
        remove_specific_item(item_pool, item)
        world.push_precollected(world.create_item(s))
    # Add duplicate stages
    for i in range(world.options.dupe_stage_count.value):
        for s in stageList:
            item_pool.append(world.create_item(s))
    return item_pool

# The item pool after starting items are processed but before filler is added, in case you want to see the raw item pool at that stage
def before_create_items_filler(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    # Use this hook to remove items from the item pool
    itemNamesToRemove: list[str] = [] # List of item names
    heart = 0
    while heart < world.options.friend_heart_amount.value - 10:
        item_pool.append(world.create_item("Friend Heart"))
        heart += 1
    heart = 0
    while heart < world.options.extra_friend_hearts.value:
        item_pool.append(world.create_item("Friend Heart"))
        heart += 1
    piece = 0
    while piece < (world.options.heart_spear_piece_amount.value - 2)*4:
        item_pool.append(world.create_item("Heart Spear Piece"))
        piece += 1
    piece = 0
    while piece < world.options.extra_heart_spear_pieces.value:
        item_pool.append(world.create_item("Heart Spear Piece"))
        piece += 1
    spice = 0
    while spice < world.options.extra_spice_levels.value:
        item_pool.append(world.create_item("Ultimate Spice Level UP"))
        spice += 1

    # Establish unified stage dictionaries
    moonDict = {
        "Planet Earthfall - Clear": "Falluna Moon", 
        "Planet Misteen - Clear": "Mareen Moon",
        "Planet Caverna - Clear": "Grott Moon",
        "Planet Frostak - Clear": "Blizzno Moon",
        "Planet Towara - Clear": "Gabbel Moon",
        "Star Lavadom - Clear": "Sizzlai Moon",
        "Jambandra Base - Clear": "The Divine Terminus"
        }
    exDict = {
        "Honey Hill - Big Switch": "Extra Eclair",
        "Reef Resort - Big Switch": "Inside Islands",
        "Nature's Navel - Big Switch": "Duplex Dream",
        "Eastern Wall - Big Switch": "Sector A",
        "Western Outer Wall - Big Switch": "Sector B",
        "Inner Sanctum - Big Switch": "Sector C",
        "Planet Misteen - Big Switch": "Extra Planet Alpha",
        "Planet Frostak - Big Switch": "Extra Planet Beta",
        "Star Lavadom - Big Switch": "Extra Planet Gamma"
        }
    # Pair item names and locations together in dictionary
    unifiedPairs = {}
    for location in multiworld.get_unfilled_locations(player=player):
        if world.options.unify_dedede_metaknight.value == True:
            if location.name == "Clash at Castle Dedede - Befriend King Dedede":
                unifiedPairs.update({"King Dedede": location})
            if location.name == "Sacred Square - Befriend Meta Knight":
                unifiedPairs.update({"Meta Knight": location})
        if world.options.unify_magesisters.value == True and world.options.enable_heroes_in_another_dimension.value == True:
            if location.name == "Final Dimension - Befriend The Three Mage-Sisters":
                unifiedPairs.update({"The Three Mage-Sisters": location})
        if world.options.unify_planets_and_moons.value == True:
            for moon in moonDict:
                if location.name == moon:
                    unifiedPairs.update({moonDict[moon]: location})
        if world.options.unify_ex_stages.value == True:
            for ex in exDict:
                if location.name == ex:
                    unifiedPairs.update({exDict[ex]: location})
    # Add each item to its paired location
    for itemName in unifiedPairs:
        item = next(i for i in item_pool if i.name == itemName)
        unifiedPairs[itemName].place_locked_item(item)
        remove_specific_item(item_pool, item)
        # multiworld.push_item(unifiedPairs[itemName], item

    # Add the aid of each Heart Spear 
    if world.options.enable_heroes_in_another_dimension.value == True and world.options.hiad_all_dimensions_required.value == True:
        location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Dimension I - Clear")
        location.place_locked_item(world.create_item("First Spear's Aid"))
        location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Dimension II - Clear")
        location.place_locked_item(world.create_item("Second Spear's Aid"))
        location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Dimension III - Clear")
        location.place_locked_item(world.create_item("Third Spear's Aid"))
        location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Dimension IV - Clear")
        location.place_locked_item(world.create_item("Fourth Spear's Aid"))
    
    if world.options.unlock_allies_with_hearts.value == True:
        friendUnlockNameBeginning = "New Friend "
        friendUnlockNameEnd = " - ???? of the Stars"
        allyCount = len(abilityListTrue)
        # for item in item_pool:
        #     for abilityName in abilityListTrue:
        #         if item.name == abilityName:
        #             allyCount += 1
        for pre in world.options.start_inventory_from_pool.value:
            startPoolItem = ""
            startPoolItem = next((a for a in abilityListTrue if a == pre), "")
            if startPoolItem != "":
                allyCount -= 1
                abilityListTrue.remove(startPoolItem)
                # print(startPoolItem)
    
        print(allyCount)
        # Use this hook to remove locations from the world
        locationNamesToRemove: list[str] = [] # List of location names
        locationRemoveCount = allyCount + 1
        while locationRemoveCount <= 40:
            locationNamesToRemove.append(friendUnlockNameBeginning + str(locationRemoveCount) + friendUnlockNameEnd)
            locationRemoveCount += 1

        # Add your code here to calculate which locations to remove
        for region in multiworld.regions:
            if region.player == player:
                for location in list(region.locations):
                    if location.name in locationNamesToRemove:
                        # print(location.name)
                        region.locations.remove(location)
        # Shuffle and add allies to pool
        for a in range(allyCount):
            itemName = abilityListTrue[a]
            locationName = friendUnlockNameBeginning + str(a+1) + friendUnlockNameEnd
            location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == locationName)
            item_to_place = next(i for i in item_pool if i.name == itemName)
            location.place_locked_item(item_to_place)
            remove_specific_item(item_pool, item_to_place)

    # Add your code here to calculate which items to remove.
    #
    # Because multiple copies of an item can exist, you need to add an item name
    # to the list multiple times if you want to remove multiple copies of it.

    for itemName in itemNamesToRemove:
        item = next(i for i in item_pool if i.name == itemName)
        remove_specific_item(item_pool, item)

    return item_pool

    # Some other useful hook options:

    ## Place an item at a specific location
    # location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Location Name")
    # item_to_place = next(i for i in item_pool if i.name == "Item Name")
    # location.place_locked_item(item_to_place)
    # remove_specific_item(item_pool, item_to_place)

# The complete item pool prior to being set for generation is provided here, in case you want to make changes to it
def after_create_items(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool

# Called before rules for accessing regions and locations are created. Not clear why you'd want this, but it's here.
def before_set_rules(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after rules for accessing regions and locations are created, in case you want to see or modify that information.
def after_set_rules(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to modify the access rules for a given location

    def Example_Rule(state: CollectionState) -> bool:
        # Calculated rules take a CollectionState object and return a boolean
        # True if the player can access the location
        # CollectionState is defined in BaseClasses
        return True

    ## Common functions:
    # location = world.get_location(location_name, player)
    # location.access_rule = Example_Rule

    ## Combine rules:
    # old_rule = location.access_rule
    # location.access_rule = lambda state: old_rule(state) and Example_Rule(state)
    # OR
    # location.access_rule = lambda state: old_rule(state) or Example_Rule(state)

# The item name to create is provided before the item is created, in case you want to make changes to it
def before_create_item(item_name: str, world: World, multiworld: MultiWorld, player: int) -> str:
    return item_name

# The item that was created is provided after creation, in case you want to modify the item
def after_create_item(item: ManualItem, world: World, multiworld: MultiWorld, player: int) -> ManualItem:
    return item

# This method is run towards the end of pre-generation, before the place_item options have been handled and before AP generation occurs
def before_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is run at the very end of pre-generation, once the place_item options have been handled and before AP generation occurs
def after_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is run every time an item is added to the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be cancelled/undone in after_remove_item
def after_collect_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you add to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] += 1
    pass

# This method is run every time an item is removed from the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be first done in after_collect_item
def after_remove_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you undo the addition to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] -= 1
    pass


# This is called before slot data is set and provides an empty dict ({}), in case you want to modify it before Manual does
def before_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called after slot data is set and provides the slot data at the time, in case you want to check and modify it after Manual is done with it
def after_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called right at the end, in case you want to write stuff to the spoiler log
def before_write_spoiler(world: World, multiworld: MultiWorld, spoiler_handle) -> None:
    pass

# This is called when you want to add information to the hint text
def before_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:

    ### Example way to use this hook:
    # if player not in hint_data:
    #     hint_data.update({player: {}})
    # for location in multiworld.get_locations(player):
    #     if not location.address:
    #         continue
    #
    #     use this section to calculate the hint string
    #
    #     hint_data[player][location.address] = hint_string

    pass

def after_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:
    pass

def hook_interpret_slot_data(world: World, player: int, slot_data: dict[str, Any]) -> dict[str, Any]:
    """
        Called when Universal Tracker wants to perform a fake generation
        Use this if you want to use or modify the slot_data for passed into re_gen_passthrough
    """
    return slot_data

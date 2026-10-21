from typing import Optional
from worlds.AutoWorld import World
from ..Helpers import clamp, get_items_with_value
from BaseClasses import MultiWorld, CollectionState

import re

# Sometimes you have a requirement that is just too messy or repetitive to write out with boolean logic.
# Define a function here, and you can use it in a requires string with {function_name()}.
def overfishedAnywhere(world: World, state: CollectionState, player: int):
    """Has the player collected all fish from any fishing log?"""
    for cat, items in world.item_name_groups:
        if cat.endswith("Fishing Log") and state.has_all(items, player):
            return True
    return False

# You can also pass an argument to your function, like {function_name(15)}
# Note that all arguments are strings, so you'll need to convert them to ints if you want to do math.
def anyClassLevel(state: CollectionState, player: int, level: str):
    """Has the player reached the given level in any class?"""
    for item in ["Figher Level", "Black Belt Level", "Thief Level", "Red Mage Level", "White Mage Level", "Black Mage Level"]:
        if state.count(item, player) >= int(level):
            return True
    return False

# You can also return a string from your function, and it will be evaluated as a requires string.
def requiresMelee():
    """Returns a requires string that checks if the player has unlocked the tank."""
    return "|Figher Level:15| or |Black Belt Level:15| or |Thief Level:15|"

def spearCompletion(world: World, state: CollectionState, player: int, spearCount: str):
    if state.count("Heart Spear Piece", player) >= world.options.heart_spear_piece_amount.value * int(spearCount):
        return True
    return False

def friendHeartBalance(world: World, state: CollectionState, player: int, friendLevel: str):
    if world.options.unlock_allies_with_hearts.value == True:
        abilityListTrue: list[str] = [
            "Beam", "Beetle", "Bomb", "Cleaning", "Cook", "Cutter", "ESP", "Fighter", "Fire", "Hammer", "Ice", "Ninja", "Parasol", "Plasma", 
            "Stone", "Suplex", "Sword", "Water", "Whip", "Wing", "Yo-Yo", "Artist", "Spider", "Staff",
            "Bandana Waddle Dee", "Rick & Kine & Coo", "Marx", "Gooey", "Adeleine & Ribbon", "Dark Meta Knight", "Daroach", "Magolor", "Taranza", "Susie", 
            "Crash", "Mike", "Festival"]
        if world.options.unify_dedede_metaknight.value == False:
            abilityListTrue.append("King Dedede")
            abilityListTrue.append("Meta Knight")
        if world.options.unify_magesisters.value == False or world.options.enable_heroes_in_another_dimension == False:
            abilityListTrue.append("The Three Mage-Sisters")
        copyAbilityCount = len(abilityListTrue)
        for pre in world.options.start_inventory_from_pool.value:
            startPoolItem = ""
            startPoolItem = next((a for a in abilityListTrue if a == pre), "")
            if startPoolItem != "":
                copyAbilityCount -= 1
                abilityListTrue.remove(startPoolItem)
        copyAbilityCount = float(copyAbilityCount)
        heartRatio = float(friendLevel) / copyAbilityCount
        totalFriendHearts = int((float(world.options.ally_friend_heart_percent.value)/100.0) * world.options.friend_heart_amount.value)
        friendHeartsNeeded = int(totalFriendHearts * heartRatio)
        return state.has("Friend Heart", player, count=friendHeartsNeeded)
    return True

def dimensionOneAccess(world: World, stepCount: str):
    reqString = ""
    stepInt = int(stepCount)
    if world.options.hiad_gating_methods.value == 1 or world.options.hiad_enable_ally_restrictions.value == True:
        match stepInt:
            case 1:
                reqString += "|Fighter|"
            case 2:
                reqString += "|Fighter| AND |Bandana Waddle Dee|"
            case 3:
                reqString += "|Fighter| AND |Bandana Waddle Dee| AND |King Dedede|"
            case 4:
                # Make sure all uses check for hiadOkZap from this point on
                reqString += "|Fighter| AND |Bandana Waddle Dee| AND |King Dedede| AND |Meta Knight|"
            case 5:
                reqString += "|Fighter| AND |Bandana Waddle Dee| AND |King Dedede| AND |Meta Knight| AND |Fire|"
            case 6:
                reqString += "|Fighter| AND |Bandana Waddle Dee| AND |King Dedede| AND |Meta Knight| AND |Fire|"
    if world.options.hiad_gating_methods.value == 2:
        if reqString != "":
            reqString += " AND "
        reqString += "|Dimension I|"
    if world.options.hiad_gating_methods.value == 3 or stepInt >= 6:
        if reqString != "":
            reqString += " AND "
        reqString += "|Friend Bridge|"
    if reqString == "":
        return True
    return reqString

def dimensionTwoAccess(world: World, state: CollectionState, player: int, stepCount: str):
    reqString = ""
    stepInt = int(stepCount)
    if world.options.hiad_gating_methods.value == 1 or world.options.hiad_enable_ally_restrictions.value == True:
        match stepInt:
            case 1:
                reqString += "|Staff|"
            case 2:
                reqString += "|Staff| AND |Rick & Kine & Coo|"
            case 3:
                reqString += "|Staff| AND |Rick & Kine & Coo| AND |Marx|"
            case 4:
                reqString += "|Staff| AND |Rick & Kine & Coo| AND |Marx| AND |Gooey|"
            case 5:
                reqString += "|Staff| AND |Rick & Kine & Coo| AND |Marx| AND |Gooey| AND |Ice|"
            case 6:
                reqString += "|Staff| AND |Rick & Kine & Coo| AND |Marx| AND |Gooey| AND |Ice|"
    if world.options.hiad_gating_methods.value == 2:
        if reqString != "":
            reqString += " AND "
        reqString += "|Dimension II|"
    if world.options.hiad_gating_methods.value == 3 or stepInt >= 6:
        if reqString != "":
            reqString += " AND "
        reqString += "|Friend Train|"
    if reqString == "":
        return True
    return reqString

def dimensionThreeAccess(world: World, state: CollectionState, player: int, stepCount: str):
    reqString = ""
    stepInt = int(stepCount)
    if world.options.hiad_gating_methods.value == 1 or world.options.hiad_enable_ally_restrictions.value == True:
        match stepInt:
            case 1:
                reqString += "|ESP|"
            case 2:
                reqString += "|ESP| AND |Adeleine & Ribbon|"
            case 3:
                reqString += "|ESP| AND |Adeleine & Ribbon| AND |Dark Meta Knight|"
            case 4:
                reqString += "|ESP| AND |Adeleine & Ribbon| AND |Dark Meta Knight| AND |Daroach|"
            case 5:
                reqString += "|ESP| AND |Adeleine & Ribbon| AND |Dark Meta Knight| AND |Daroach| AND |Cleaning|"
            case 6:
                reqString += "|ESP| AND |Adeleine & Ribbon| AND |Dark Meta Knight| AND |Daroach| AND |Cleaning|"
    if world.options.hiad_gating_methods.value == 2:
        if reqString != "":
            reqString += " AND "
        reqString += "|Dimension III|"
    if world.options.hiad_gating_methods.value == 3 or stepInt >= 6:
        if reqString != "":
            reqString += " AND "
        reqString += "|Friend Circle|"
    if reqString == "":
        return True
    return reqString

def dimensionFourAccess(world: World, state: CollectionState, player: int, stepCount: str):
    reqString = ""
    stepInt = int(stepCount)
    if world.options.hiad_gating_methods.value == 1 or world.options.hiad_enable_ally_restrictions.value == True:
        match stepInt:
            case 1:
                # Make sure to check for cold if only the cutter room is accessible
                reqString += "|Cutter|"
            case 2:
                reqString += "|Cutter| AND |Magolor|"
            case 3:
                reqString += "|Cutter| AND |Magolor| AND |Taranza|"
            case 4:
                reqString += "|Cutter| AND |Magolor| AND |Taranza| AND |Susie|"
            case 5:
                reqString += "|Cutter| AND |Magolor| AND |Taranza| AND |Susie| AND |Wing|"
            case 6:
                reqString += "|Cutter| AND |Magolor| AND |Taranza| AND |Susie| AND |Wing|"
    if world.options.hiad_gating_methods.value == 2:
        if reqString != "":
            reqString += " AND "
        reqString += "|Dimension IV|"
    if world.options.hiad_gating_methods.value == 3 or stepInt >= 6:
        if reqString != "":
            reqString += " AND "
        reqString += "|Friend Star|"
    if reqString == "":
        return True
    return reqString

def hiadOkBlizzard(world: World, state: CollectionState, player: int):
    if world.options.hiad_enable_ally_restrictions.value == False:
        return True
    return "|Adeleine & Ribbon| OR |Daroach| OR |The Three Mage-Sisters| OR |Ice|"

def hiadOkBluster(world: World, state: CollectionState, player: int):
    if world.options.hiad_enable_ally_restrictions.value == False:
        return True
    # TRACK DOWN: Wing
    return "|Rick & Kine & Coo| OR |Magolor| OR |Cleaning| OR (|Wing| AND ( ({dimensionThreeAccess(6)}) ))"

def hiadOkSplash(world: World, state: CollectionState, player: int):
    if world.options.hiad_enable_ally_restrictions.value == False:
        return True
    # TRACK DOWN: Parasol, Water
    return "|Rick & Kine & Coo| OR |Gooey| OR |The Three Mage-Sisters| OR |Cleaning| OR (|Parasol| AND ( ({dimensionTwoAccess(6)}) OR ({dimensionThreeAccess(2)}) )) OR (|Water| AND ( (({dimensionOneAccess(4)}) AND ({hiadOkZap()})) OR ({dimensionTwoAccess(3)}) OR ({dimensionFourAccess(3)}) ))"

def hiadOkCold(world: World, state: CollectionState, player: int):
    return "{hiadOkBlizzard()} OR {hiadOkBluster()} OR {hiadOkSplash()}"

def hiadOkSizzle(world: World, state: CollectionState, player: int):
    if world.options.hiad_enable_ally_restrictions.value == False:
        return True
    # TRACK DOWN: Fighter
    return "|Rick & Kine & Coo| OR |Gooey| OR |Daroach| OR |Magolor| OR |The Three Mage-Sisters| OR |Fire| OR (|Fighter| AND ( ({dimensionOneAccess(0)}) OR ({dimensionThreeAccess(6)}) ))"

def hiadOkHeat(world: World, state: CollectionState, player: int):
    return "{hiadOkSizzle()} OR |Cook|"

def hiadOkZap(world: World, state: CollectionState, player: int):
    if world.options.hiad_enable_ally_restrictions.value == False:
        return True
    # TRACK DOWN: Beam, ESP
    return "|Adeleine & Ribbon| OR |Daroach| OR |Magolor| OR |Taranza| OR |The Three Mage-Sisters| OR |Plasma| OR (|ESP| AND ( ({dimensionTwoAccess(2)}) OR ({dimensionThreeAccess(0)}) )) OR (|Beam| AND ( ({dimensionOneAccess(3)}) OR ({dimensionTwoAccess(1)}) ))"

def hiadOkGeo(world: World, state: CollectionState, player: int):
    if world.options.hiad_enable_ally_restrictions.value == False:
        return True
    return "|Stone| OR |Rick & Kine & Coo| OR |Gooey|"

def geoCurling():
    return "|@Geo| AND (|@Blizzard| OR |@Splash| OR |Cleaning|)"

def geoKinesis():
    return "|@Geo| AND |ESP|"

def betterThrowAbilities():
    return "|Magolor| OR |The Three Mage-Sisters|"

def throwBlockCommon():
    return "|@Friend Throw| OR ({geoKinesis()}) OR ({geoCurling()})"

def throwBlockClean():
    return "|@Friend Throw| OR ({geoKinesis()}) OR (|@Geo| AND |Cleaning|)"

def throwBlockHard():
    return "|@Friend Throw| OR ({geoKinesis()})"

def longviewBreakers():
    return "({geoKinesis()}) OR ({geoCurling()}) OR ({betterThrowAbilities()})"

def tallGrassCommon():
    return "|@Cut| OR |@Sizzle| OR |Cook| OR |@Paint| OR (|@Bluster| AND |Marx|) OR (|Water| AND |@Blizzard|)"

def burningChain():
    return "(|@Elemental Cut| AND |@Cold|) OR (|@Bluster| AND |Marx|) OR (|Water| AND |@Blizzard|)"

def hasMain(world: World, state: CollectionState, player: int):
    mainReqString = ""
    mainList = world.options.uc_ensure_strong_ally.value

    for i in range(len(mainList)):
        mainReqString += ("|" + mainList[i] + "|")
        if i < (len(mainList) - 1):
            mainReqString += " OR "
    return mainReqString

def allSpearsAssembled():
    return "|Friend Train| AND |Friend Circle| AND |Friend Star| AND |Friend Bridge| AND ({spearCompletion(4)})"

def heartPiercer(world: World, state: CollectionState, player: int):
    if world.options.hiad_all_dimensions_required.value == True:
        return "|First Spear's Aid| AND |Second Spear's Aid| AND |Third Spear's Aid| AND |Fourth Spear's Aid|"
    return True
# Object classes from AP that represent different types of options that you can create
from Options import Option, FreeText, NumericOption, Toggle, DefaultOnToggle, Choice, TextChoice, Range, NamedRange, OptionGroup, PerGameCommonOptions, OptionList
# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value
from ..Items import item_name_groups
from typing import Type, Any


####################################################################
# NOTE: At the time that options are created, Manual has no concept of the multiworld or its own world.
#       Options are defined before the world is even created.
#
# Example of creating your own option:
#
#   class MakeThePlayerOP(Toggle):
#       """Should the player be overpowered? Probably not, but you can choose for this to do... something!"""
#       display_name = "Make me OP"
#
#   options["make_op"] = MakeThePlayerOP
#
#
# Then, to see if the option is set, you can call is_option_enabled or get_option_value.
#####################################################################


# To add an option, use the before_options_defined hook below and something like this:
#   options["total_characters_to_win_with"] = TotalCharactersToWinWith
#
class TotalCharactersToWinWith(Range):
    """Instead of having to beat the game with all characters, you can limit locations to a subset of character victory locations."""
    display_name = "Number of characters to beat the game with before victory"
    range_start = 10
    range_end = 50
    default = 50

class FillerItemList(OptionList):
    """
    What filler items should be used for this game?
    Adding the same name multiple times increases its weight in the random pool. 
    Besides the amiibo items (if you have them), this is purely cosmetic and up to player/host discretion.
    
    The following is a list of all the valid filler item names. How/if you decide to use each of these is entirely up to you!
    FILLER NAMES: Standard Amiibo, Kirby/BoxBoy Series Amiibo, Yellow Point Star, Green Point Star, Red Point Star, Blue Point Star, Tomato, 
            Apple, Strawberry, Cherry, Car Mouth Cake, Pep Brew, Bead, Star Coin, Starry Coin, Stamp Ticket, Picture Piece, Clay Figurine, 
            Enemy Info Card, Gummy, Keychain, Sticker, Gotcha Figure, Character Treat
    SPECIAL FILLER NAMES: 1-Up, Maxim Tomato, Invincible Candy, Attack Power-Up Heart, Health Power-Up Heart, Speed Power-Up Heart, 
            All Power-Up Heart, Mint Leaf, Sweet Potato, Superspicy Curry, Gem Apple, Fire Fragment, Water Fragment, Light Fragment, 
            Rare Fragment, Apple Sherbet, Strawberry Shortcake, Deluxe Rainbow Parfait, Eclair, Rare Stone
    """
    valid_keys = item_name_groups["Filler Pool"]
    defPool: list[str] = ["Standard Amiibo", "Standard Amiibo", "Kirby/BoxBoy Series Amiibo"]
    default = defPool

class EnableUltimateChoice(Choice):
    """
    Should bosses from the Ultimate Choice yield checks?
    Note that if the goal involves Ultimate Choice, you will still need to defeat the specified end boss (Void Soul or Astral Birth Void)
    """
    option_disabled = 0
    option_enabled = 1
    option_enabled_include_soul_melter = 2
    option_enabled_include_soul_melter_ex = 3
    default = 1


class ToughStarAllies(OptionList):
    """
    Should there be any allies that are deemed mandatory for the hardest endurance challenges?
    Affected locations include the Ability Planet Enemy Gauntlet rewards and both versions of Soul Melter.
    Ensures that at least one of the listed allies will be obtainable prior to any of these locations.

    If you don't have an ability/dream friend preference, feel free to leave this option blank.
    """
    valid_keys = item_name_groups["Ally"]
    defAllies: list[str] = ["Marx", "Adeleine & Ribbon", "Dark Meta Knight", "Magolor", "Taranza", "The Three Mage-Sisters"]
    default = defAllies

# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict[str, Type[Option[Any]]]) -> dict[str, Type[Option[Any]]]:
    options["filler_item_pool"] = FillerItemList
    options["enable_ultimate_choice"] = EnableUltimateChoice
    options["uc_ensure_strong_ally"] = ToughStarAllies
    return options

# This is called after any manual options are defined, in case you want to see what options are defined or want to modify the defined options
def after_options_defined(options: Type[PerGameCommonOptions]):
    # To access a modifiable version of options check the dict in options.type_hints
    # For example if you want to change DLC_enabled's display name you would do:
    # options.type_hints["DLC_enabled"].display_name = "New Display Name"

    #  Here's an example on how to add your aliases to the generated goal
    # options.type_hints['goal'].aliases.update({"example": 0, "second_alias": 1})
    # options.type_hints['goal'].options.update({"example": 0, "second_alias": 1})  #for an alias to be valid it must also be in options

    pass

# Use this Hook if you want to add your Option to an Option group (existing or not)
def before_option_groups_created(groups: dict[str, list[Type[Option[Any]]]]) -> dict[str, list[Type[Option[Any]]]]:
    # Uses the format groups['GroupName'] = [TotalCharactersToWinWith]
    groups['The Ultimate Choice'] = [EnableUltimateChoice, ToughStarAllies]
    return groups

def after_option_groups_created(groups: list[OptionGroup]) -> list[OptionGroup]:
    return groups

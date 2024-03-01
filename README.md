# Contanki: Controller Support for Anki

Contanki is an add-on for [Anki](https://apps.ankiweb.net) which allows users to control Anki using a gamepad or other controller device. To install, visit [AnkiWeb](https://ankiweb.net/shared/info/1898790263) or use the install code 1898790263.

Features:
 - Comfortably review your cards using a gamepad - no more sore hands, backs, or eyes!
 - Control almost any Anki feature without a keyboard or mouse
 - Pull up a helpful overlay to remind you of the control mapping
 - Cursor control for limited situations where the gamepad is insufficient
 - Fully customisable control bindings
 - Much more!

 <img src="screenshots/Main.png" width="800">

## Usage Notes
Connect your controller via USB or Bluetooth, install the add-on, restart Anki, and press any button to get started.

Controls can be reassigned using the add-on's config dialog. You can assign controls for each context (review, deck browser, etc), as well as global settings that are used if a control isn't assigned to a particular context. It is suggested that you try the default control bindings to begin with, and make changes as needed. Since Anki has a lot of functions to map, Contanki features a quick select menu, which by default is shown using the right trigger. This will also pull up an overlay showing the control bindings for the current screen. You can remove any actions you don't need if the controls overlay is too cluttered.

Support is provided for 2.1.45 and above, but please note the version specific issues below. 

### Analog Sticks
By default the right stick is used to move and click the mouse, and you can use L2 + right stick for a secondary click. It is only possible to click within Anki. The left stick is used to scroll and to navigate between views. Sticks can be reassigned and can also be put in 'button mode', where actions can be assigned to the directions of a stick.

### Choosing a Controller
I have been testing using a DualShock 4, which  makes a good choice and can be readily purchased secondhand at a reasonable price. The cheapest option would be a knockoff SNES controller, which can be found for $10 or less.

Currently it is only possible to use a single controller at a time. This may include Joy-Cons depending on your system, but support for using both Joy-Cons is planned.

## Testing
I'm now looking for beta testers - download the latest beta release and let me know how it goes. Please report all issues on the GitHub issue tracker. Reports about bugs on Windows or when using an Xbox controller are particularly welcome as I have been testing almost exclusively on Mac using a DualShock 4 up to now. 

If you encounter an issue, let me know what you were trying to do, what platform and controller you're using, and the text of any error or message your receive. Please take note of the known issues and don't report anything listed there. Suggestions are also welcome, and should also be raised on the issue tracker.

## Known issues
 - Interaction outside of the main window (especially the browser and preferences) is only partially implemented
 - Clicking outside Anki or in the title or menu bars doesn't work 
 - Add-on doesn't function in the profile window
 - Unable to open or close webview context menus

Version Specific:
 - Due to changes in Anki's toolkit, only version 2.1.66 and beyond are supported. Older versions of the add-on can be found on GitHub for older versions of Anki back to 2.1.45.

Platform Specific
 - Volume controls only work on MacOS

Controller Specific
 - Using both Joy-Cons at once might be buggy.
 - 8BitDo controllers should be set to X mode. More info [here](https://support.8bitdo.com)
 - If your 8BitDo controller isn't detected correctly try Tools > Controller Options > Detect 8BitDo Controllers
 - Steam Deck might not work at all

Add-on compatibility
 - Not compatible with:
    - Anjoy
 - Has issues:
    - Customize Keyboard Shortcuts - a small number of actions rely on simulating a key press, and won't work if you've changed that shortcut. Instead you can create a custom action in the controller options using your assigned shortcut

## Development log

### Version 1.0.2
 - Fix axes actions not triggering

### Version 1.0.1
 - Fix crash due to missing buttons

### Version 1.0
 - Add support for 8BitDo Lite 2
 - Add action to toggle Image Occlusion masks
 - Limit height of config dialog
 - Fix crash when controller doesn't present enough axes
 - Arbitrarily decided to move out of beta!

### Beta 23
 - Handle Switch Pro 'ghost' controllers
 - Fix crash if empty custom action exists
 - Fix D-pad not working in quick select

### Beta 22
 - Add support for 8BitDo Micro.
 - Fix Joy Con axes and connection bugs
 - Sort actions alphabetically
 - Add support for smooth button scrolling

### Beta 21
Fix missing custom_controllers folder

### Beta 20
Fixes buttons not flashing for some users when pressed in config dialog 

### Beta 19
Tentative fix for 8BitDo D-Pad issues

### Beta 18
This beta adds a new tab to the config allowing users to fix issues with their controller mappings. It should be considered very much a beta feature and has not yet been extensively tested.

### Beta 17
 - Axis buttons now appear overlay (other axis assignments still don't appear)
 - Fix axis assignments not being recognised when multiple axes are assigned the same axis

### Beta 16
 It's been a while! Finally had time to pull it together and get an update out. Unfortunatly while a lot of issues are easy to fix, getting an update out involves a lot of testing to make sure new bugs haven't be introduced, and I keep starting without finishing.
 - Support for 8BitDo Ultimate
 - Tentative support for Steam Deck
 - Option to invert axes
 - Added option to export and import profiles
 - Cursor now controllable accross multiple screens
 - Various bug and crash fixes

Due to changes in Anki's toolkit, only version 2.1.66 and beyond are supported. Older versions of the add-on can be found on GitHub for older versions of Anki back to 2.1.45.

### Beta 15

 - Fix config not saving profile changes under some circumstances
 - Some some users upgrading from an older version loading old profile versions

### Beta 14

 - Fix profile changes not being saved/profiles being overridden by defaults
 - Update Switch Pro button mappings
 - Deadzone and acceleration changes take effect without restart

Apologies for leaving the saving bug unfixed for so long.

### Beta 13

 - Improved compatibility with Joy-Cons
 - Improved compatibility with 8BitDo Zero and Pro
 - Fix several profiles bugs in the config menu
 - Make overlay transparent to mouse events
 - Various other fixes

### Beta 12

 - Fix crash when opening config if no controller is connected
 - Fix inherited actions not saving
 - Added configuration option to detect 8BitDo controllers

### Beta 11

 - Fix crash if vendor or device ID not extracted (actually fixed this time!)
 - Fix crash if invalid file in user profiles folder
 - Fix DS4 incorrectly detected as 8BitDo Pro

### Beta 10 

 - Fix custom actions not being triggered
 - Fix quick select icon bug for Joy-Cons + Steam Controllers
 - Fix crash if vendor or device ID not extracted
 - Fixes to default profiles

### Beta 9

Minor fixes to controllers detection + button mappings.

### Beta 8

As with Alpha 11, this release does away with modifier keys and introduces a 'quick select' menu for accessing additional actions. A button can be assigned to show the quick select menu (either while held or to toggle it) and the action can be selected using the left stick or d-pad. The actions that appear in the menu are chosen in the config. The menu can currently hold a maximum of 8 actions, but this limit should be raised in a future update when using the stick to select.

Many other parts of the codebase have been rewritten for this release compared with the last beta, aimed at fixing bugs, improving compatibility, and making the add-on more stable, but due to the extent of the changes it's likely at least a couple of bugs have been introduced. I'll be focused on bug fixing from now, including controller compatibility, since I think all the features I want are pretty much done.

I'll leave this up on here for a couple of days before uploading to AnkiWeb in case any major bugs crept in.

### Beta 7
Hotfix release to fix a bug relating to annotations not being available for some users. 

Other fixes:
 - Fix freeze when selecting due decks but none due
 - Tentative fix for crash on 8BitDo Zero auto power off

### Beta 6
Improvements:
 - When a button icon can't be found, a fallback text icon will now be generated
 - Improved controller detection code and added various controllers to the list 
 - The help button in the config now provides debug data and additional advice 
 - Implemented testing module and began to add tests

Fixes:
 - Fix layout error and added direct input mode for 8BitDo Zero
 - Fixed icon issue for Dualshock 3 on Linux
 - Fix mouse movement not working on some Linux versions
 - When selecting a different controller in the controls tab, the options tab is now updated immediately
 - Profile saving no longer fails if the profile name contains illegal characters
 - Incompatibility with the Enhance Main Window add-on has been fixed on their end

### Beta 5
Changes:
 - Further fixes for controller connection handling
 - Fix for current controller requiring reconnection when a different controller was disconnected
 - Improvements to handling multiple connected controllers
 - Default controls layout no longer duplicates 'Suspend Card' at the expense of 'Suspend Note'

### Beta 4
Hotfix for certain controllers causing an error when connected. 

### Beta 3
Changes:
 - Implement cursor deadzone setting and add deadzone to scrolling (thanks to@AuroraWright)
 - Improved controller detection
 - Fixes to deck navigation when collection only has one deck

### Beta 2
Changes:
 - Adds buttons for the Steam Deck and 8BitDo Zero and Lite
 - Fixed an error when opening the config dialog without a controller connected
 - Fixed an issue where the config dialog wasn't accessible when opened from the add-ons dialog
 - Fixed config button icons not glowing when button pressed
 - Fixed error on profile save when selected controller has fewer axes than profile

### Beta 1
It's here!

Changes since Alpha 10:
 - Various actions trigger tooltips instead of popups when they fail (undo, redo, empy, rebuild)
 - Some other improvements to how actions errors are handled
 - Improved support for older versions back to 2.1.45

 You can now find it on AnkiWeb.

### Alpha 10
 - Improved deck navigation
 - Fix for certain actions occuring when Anki not focused
 - If a user action triggers an error, this will now be captured and show in a tooltip

 Anki 2.1.50 is likely to drop soon, and I'm aiming to release a beta at the same time. 


### Alpha 9
 - If multiple controllers are plugged in, the user can now select which one to use. Some controllers may present themselves multiple times (presumably for compatibility reasons)
 - Default profiles have been added to all supported controllers

### Alpha 8

 - Profile buttons are now functional, allowing you to add, delete, and rename profiles. 
 - Mouse and scroll behaviour can now be customised. 
 - Added option to disable or use large overlays. 
 - Various fixes.

I need to create default profiles for some remaining controllers, and if I don't find any more bugs I'll release a beta.

### Alpha 7

Smaller hotfix release, mostly fixing controller compatibility and config dialog issues. The buttons in the config dialog now light up when you press the corresponding button on your controller.

### Alpha 6

This release adds a number of features:
 - Sticks can now be put in button mode, allowing actions to be assigned to directions on the stick
 - Custom actions can now be created and assigned
 - Custom modifiers can now be assigned
 - Almost all supported controllers have fully functional config screens (although I still need to confirm the button layouts and set up default profiles on some of them)

This release does away with the old overlay in favour of individual icons for each button. I did like the old overlays, but it proved to be impractical to support more than a handful of controllers, as well as making it hard to display the assignments of sticks in button mode. The new system is much better in a lot of ways.

There's a few more issues to tidy up before a beta can be released, but it's close to feature complete so I'm mostly just tidying up at this point. Anki 2.1.50 now has a release candidate so hopefully we'll see a release in a few weeks.

### Alpha 5

The config dialog is now functional, opening up a lot of new features in the process. Different profiles can now be created, the controls are now more customisable, and many controllers are now autodetected and will work out of the box. Axes can be reassigned, control inheritence is now visible to the user, and users can control which controller is displayed on the overlays.

Certain features are not yet fully implemented:
 - Custom modifier keys cannot yet be assigned
 - Custom actions cannot yet be created or assigned
 - Actions cannot be assigned to analog sticks in button mode
 - Not all controllers have default profiles yet
 - Some controllers still lack finished config screens
 - Certain configuration options are not yet functional

These should all be relatively easy to implement now that the underlying profile module is functional. 

I've made further progress on the dialogs issue, and it's likely that dialog access will be basically functional with only limited exceptions in Anki 2.1.50. 

With this release earlier versions of Anki now work, however a new issue has cropped up with certain controllers presenting themselves multiple times, which causes various issues. It's likely I'll have to add support for choosing which controller to use to resolve this.

For the next release I'm aiming to add support for custom actions and modifiers, finish the controls screens and default profiles for all supported controllers, and connect the remaining options. That should cover all the key features and once 2.1.50 releases I'll hopefully be ready release a beta.

### Alpha 4

This release demos the new config dialog, although right now it's not actually functional. I've been implementing the module for handling profiles that will save your controller layouts, and I really want that to be locked down because changes to it might break people's profiles which would be a huge pain. Along with the new config dialogs comes various features for detecting consoles, support for different controllers, new options to configure, and more, but for these to be put to use the main code for handling controls now needs to be updated to use these. I wanted to push out this release before I start.

There's still a problem with 2.1.48 and below, which I've put off investigating since the upcoming refactor to the main controller code might well fix it . Right now the latest 2.1.50 beta works best, but 2.1.49 works fine as well. More controllers should now work, although proper support for the full range of controllers will come in the next release once the new profile and control mapping module is fulling implemented.

Speaking of which, I've also been working on resolving the dialog on Anki's end by submitting pull requests to fix the affected dialogs and menus one by one. You can now see the results of this on the latest Anki beta, with the deck selector, custom study, and deck configuration dialogs now navigable using Contanki. I'll work on the context menus next. I plan to make this issue a priority in the hope that can be fully or largely resolved by the time of the 2.1.50 release.

### Alpha 3

Alpha 3 is now available for download. Unfortunately it only supports 2.1.49 and 2.1.50, but this should be fixed in the next release.

New features
 - Greatly improved dialog interaction (although see below regarding the dialog/menu issue)

Fixes:
 - Message shown on controller disconnect
 - Reconnects now more reliable
 - Tentative fix for excessive CPU usage if Anki has been left open for several days
 - Compatibility fixes for earlier Anki versions (but most testing is still on 49 & 50 so far)
 
 I've been working on fixing the dialogs/menus .exec() issue, but the fixes required are in Anki's code, so it's unlikely this issue will be addressed for any current version of Anki, and it requires changes to each individual menu or dialog and a lot of testing to ensure it doesn't introduce other issues, so is likely to take some time. This add-on won't be moved to beta until these fixes make it to a main Anki release.

In the meantime users will simply have to avoid clicking the menus or opening affected dialogs. I might release a version with those features disabled, but for testing purposes they are enabled in alpha versions.

Both clicking outside Anki and touchpad support are low priority right now, as they are both likely to require a lot of work and possibly different solutions for each platform. I do intend to eventually support both however.

The following features are intended before the beta release:

 - Improved config dialog
 - Controller profiles
 - Full support for Xbox controllers
 - All actions configurable
 - Compatibility back to 2.1.45 (probably without dialog access)
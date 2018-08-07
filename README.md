# lewansoul-lx-16a

GPLv3

# Who

Not really important - I guess check "Contributors" if this matters to you

# What

An application implemented in PYQT5 for configuring LewanSoul LX-16A bus servos.
Will include some control features for positioning servos, but that's not it's real point.

The goal is servo setup.

# When

Soonish?

I started last night after spending maybe 15 minutes going through a few tutorials on <a href="http://zetcode.com/gui/pyqt5">ZetCode</a>, so I imagine this will be done by the end of the week?

Immediately ran into serial connection issues, but I think I've got those sorted now.  Just the sort of progress to build momentum.

# Why

The download on LewanSoul's website to configure my new servos doesn't play well with Linux.  In fact, can't load it through wine at all, although I don't blame wine.  To be fair, the installer and uninstaller work.
Not finding a linux version in my searches, and I'll need to write most of what this program will do into my REAL project anyway, so why not build a PYQT5 version to share?
Also, hoping put the code out will help someone else if they want to create their own program for working with these servos.

# How

First things first, top three priorities:

* Polling bus for attached servos (done-ish)
* Setting device ID's
* Setting/Reading positions
* Setting/Reading servo error conditions

(Yes, that IS four, you're probably only slightly crazy)



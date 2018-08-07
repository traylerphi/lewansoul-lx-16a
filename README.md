# lewansoul-lx-16a

GPLv3

# Why

The download on LewanSoul's website to configure my new servos doesn't play well with Linux.  In fact, can't load it through wine at all.  Not finding a linux version in my searches, and I'll need to write most of what this program will do into my REAL project anyway, so why not build a PYQT5 version to share?

# When

There is the minor issue of this being my first PYQT5 application, although I just spent maybe 15 minutes going through a few tutorials on <a href="http://zetcode.com/gui/pyqt5">ZetCode</a>, so I imagine it'll be fine.

Then there's deciphering the sometimes humorous language of the documentation LewanSoul provides.  Reminds me of my Assembly days, so the protocol doesn't look TOO duanting.  Figure the biggest challenge here will be actually accessing the Debug Board through USB; all downhill after that.

So... soonish? If I don't have at least some basic stuff going by week's end (let's say 2018-08-10) then this is probably already a dead project...

# The Plan

First things first, top three priorities:

* Setting device ID's
* Polling bus for attached servos
* Setting/Reading positions
* Setting/Reading servo error conditions

(Yes, that IS four, you're probably only slightly crazy)



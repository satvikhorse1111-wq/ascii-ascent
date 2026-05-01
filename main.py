from mainmode import MainMode

r"""       
  m   .m,   mm  mmm  mmm        m   .m,   mm .mmm,.m .,.mmm,
 ]W[ .P'T  W''[ 'W'  'W'       ]W[ .P'T  W''[]P''`]W ][''W'`
 ]W[ ]b   ]P     W    W        ]W[ ]b   ]P   ][   ]P[][  W  
 W W  TWb ][     W    W        W W  TWb ][   ]WWW ][W][  W  
 WWW    T[]b     W    W        WWW    T[]b   ][   ][]d[  W  
.W W,]mmd` Wmm[ mWm  mWm      .W W,]mmd` Wmm[]bmm,][ W[  W  
'` '` ''`   ''  '''  '''      '` '` ''`   '' ''''`'` '`  '
ASCII Ascent: A Platformer Game [Capybara Studios (C) 2026]
"""

# Checklist [in order]:

# - Refactor everything as needed. DOCUMENT EVERYTHING.
# -- Add * and / into function arguments while you are at it
# -- ADD CONSTANTS. Such as: 12 x 63, default arguments, etc.
# -- Fix the interface for Endless, with the mode, spikes, asterisks variables.

# - Delete 'secret'
# - Get it playtested

# Ideas for next update:
# - Portals for changing game modes?
# - Blindfold mode

__version__ = "1.0"

if __name__ == "__main__":

    MainMode().run()

from base.run import run_private
from bot2 import make_move

userid = "sdlfkjsdlfk"  # Anonymous if random string. Public tester bot if empty. To log in check dev console at bot.generals.io.
username = "[Bot] dsgfhj"  # Only used if the logged in account still does not have a username.
roomid = "40mt"  # id from url to join and random string to create

run_private(make_move, userid, roomid, username)

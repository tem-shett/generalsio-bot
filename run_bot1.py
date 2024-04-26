from base.run import run_private, run_1v1
from bot import make_move

userid = "dfgdfhdgsfdsf"  # Anonymous if random string. Public tester bot if empty. To log in check dev console at bot.generals.io.
username = "[Bot] Artyom_bot"  # Only used if the logged in account still does not have a username.
roomid = "40mt"  # id from url to join and random string to create

run_private(make_move, userid, roomid, username)
# run_1v1(make_move, userid, username)

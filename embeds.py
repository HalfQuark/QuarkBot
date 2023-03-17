import datetime

import discord

import tickets


def siegeembed(client, arr):
    today = datetime.date.today()
    d = today + datetime.timedelta((int(arr[1]) - today.weekday()) % 7)
    t = datetime.time(hour=int(arr[2][0:2]), minute=int(arr[2][2:4]))
    dtime = datetime.datetime.combine(date=today, time=t)
    embed = discord.Embed(title=arr[0].replace("_", " "),
                          color=0x666666,
                          timestamp=dtime)
    embed.set_footer(text=d)
    # Add author, thumbnail, fields, and footer to the embed
    embed.set_thumbnail(url=client.user.avatar_url)

    embed.add_field(name="Cost to siege", value=arr[3], inline=True)
    embed.add_field(name="Profit per day", value=arr[4], inline=True)
    embed.add_field(
        name="Siege window",
        value=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][int(arr[1])] +
        " at " + str(t) + " UTC",
        inline=False)
    embed.add_field(name="Next siege", value="(Time converted to your timezone below, ignore \"Today at\")")
    return embed


def ticketembed(member):
    embed = discord.Embed(title=member.display_name,
                          color=0x666666)
    # Add author, thumbnail, fields, and footer to the embed
    embed.set_thumbnail(url=member.avatar_url)

    embed.add_field(name=f"{tickets.get(member.id)} 🎟", value="-", inline=True)
    return embed

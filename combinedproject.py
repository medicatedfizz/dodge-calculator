import requests
from urllib import parse
from discord.ext import commands
import os

# 욕안하면사람아님님이 로비에 참가하셨습니다.
# 내이름은메이님이 로비에 참가하셨습니다.
# 20171340님이 로비에 참가하셨습니다.
# 도마뱀 동동이님이 로비에 참가하셨습니다.
# 자취하는여고생님이 로비에 참가하셨습니다.


api_key = os.environ['RIOTAPI']


def nickname_separator(names_):
    summoner_nicknames = []
    for a in names_:
        b = a.replace("님이 로비에 참가하셨습니다.", "")
        summoner_nicknames.append(b)
    return summoner_nicknames   # list


def encrypt_id(APIKEY, summonerName):
    summonername_url = parse.quote(summonerName)
    APIURL = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonername_url
    headers = {
        "Origin": "https://developer.riotgames.com",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Riot-Token": APIKEY,
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                      " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }
    res = requests.get(APIURL, headers=headers)
    data = res.json()
    return data["id"], data["puuid"]   # str


def total_winrate(APIKEY, id_lol):
    urlid = parse.quote(id_lol)
    APIURL = "https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/" + urlid
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://developer.riotgames.com",
        "X-Riot-Token": APIKEY
    }
    res = requests.get(APIURL, headers=headers)
    data = res.json()
    data_dic = None
    for game in data:
        if game["queueType"] == "RANKED_SOLO_5x5":
            data_dic = game
    if data_dic is None:
        data_dic = "솔로 랭크 전적이 없습니다."
        return data_dic
    tot_winrate = data_dic["wins"]/(data_dic["wins"] + data_dic["losses"])
    return round(tot_winrate*100, 2)      # int


def match_encrypted(APIKEY, puuid_lol):
    puuid_url = parse.quote(puuid_lol)
    APIURL = "https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuid_url + \
             "/ids?type=ranked&start=0&count=20"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://developer.riotgames.com",
        "X-Riot-Token": APIKEY
    }
    res = requests.get(APIURL, headers=headers)
    data = res.json()
    return data   # list로 나옴


def recent_match_info(APIKEY, match_list, summonerId):
    data_wins = []
    data_kills = []
    data_deaths = []
    data_assists = []
    kda_list = []
    solorank_info = []
    win_num = 0
    ranked_solo_count = 0
    no_matches = "최근 전적이 없습니다."
    for j in match_list:
        match_info_url = parse.quote(j)
        APIURL = "https://asia.api.riotgames.com/lol/match/v5/matches/" + match_info_url
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://developer.riotgames.com",
            "X-Riot-Token": APIKEY
        }
        res = requests.get(APIURL, headers=headers)
        data = res.json()
        data_get = data.get("info")
        try:
            if data_get["queueId"] == 420:
                solorank_info.append(data_get)
                ranked_solo_count += 1
            if ranked_solo_count >= 10:
                break
        except TypeError:           # 가끔 오류인지 data_get["queueId"] 인덱싱이 실패해서 try except를 씀
            continue
    if ranked_solo_count == 0:
        return no_matches, no_matches
    for round_num in solorank_info:
        for k in range(10):
            if round_num["participants"][k]["summonerId"] == summonerId:
                data_wins.append(round_num["participants"][k]["win"])
                data_kills.append(round_num["participants"][k]["kills"])
                data_deaths.append(round_num["participants"][k]["deaths"])
                data_assists.append(round_num["participants"][k]["assists"])
    for m in range(ranked_solo_count):
        try:
            kda_calculation = round((data_kills[m] + data_assists[m])/data_deaths[m], 2)
            kda_list.append(kda_calculation)
        except ZeroDivisionError:
            kda_calculation = "Perfect"
            kda_list.append(kda_calculation)
    print(kda_list)
    for n in data_wins:
        if n:
            win_num += 1
    try:
        recent_10_kda_tot = round((sum(data_kills) + sum(data_assists))/sum(data_deaths), 2)
    except ZeroDivisionError:
        recent_10_kda_tot = "Perfect"
    return round((win_num/ranked_solo_count)*100, 2), recent_10_kda_tot  # tuple, 내부는 int


def kda_score_translator(kda_10):
    sum_winrate = []
    kda_to_winrate = None
    for kdas in kda_10:
        if isinstance(kdas, float):
            if kdas <= 0.5:
                kda_to_winrate = 10
            elif kdas <= 1.5:
                kda_to_winrate = 25
            elif kdas <= 2.5:
                kda_to_winrate = 35
            elif kdas <= 3:
                kda_to_winrate = 50
            elif kdas <= 5:
                kda_to_winrate = 70
            elif kdas > 5:
                kda_to_winrate = 100
        elif kdas == "Perfect":
            kda_to_winrate = 100
        else:
            kda_to_winrate = 50            # kdas = "최근 전적이 없습니다"
        sum_winrate.append(kda_to_winrate)
    return sum_winrate


def dodge_calculator(tot_win, kda_10, winrate_10):
    tot_win_sum = 0
    winrate_10_sum = 0
    for (u, p) in zip(tot_win, winrate_10):             # 만약 tot_win = "솔로 랭크 전적이 없습니다" 거나
        if isinstance(u, float):                        # winrate_10 = "최근 전적이 없습니다" 이면
            tot_win_sum += u                            # 두 경우 모두 승률을 50%로 계산
        elif isinstance(u, str):
            tot_win_sum += 50
        if isinstance(p, float):
            winrate_10_sum += p
        elif isinstance(p, str):
            winrate_10_sum += 50
    avg_tot_win = tot_win_sum/len(tot_win)
    print(avg_tot_win)
    avg_winrate_10 = winrate_10_sum/len(winrate_10)
    print(avg_winrate_10)
    avg_kda_10 = sum(kda_10)/len(kda_10)
    print(avg_kda_10)
    dodge_winrate = 0.5*avg_tot_win + 0.25*avg_winrate_10 + 0.25*avg_kda_10
    print(f"이번 판의 승률은 {dodge_winrate}입니다.")
    if dodge_winrate < 50:
        print("닷지를 추천드립니다.")
    else:
        print("승률이 50퍼센트 이상입니다.")
    return dodge_winrate


# discord bot
bot = commands.Bot(command_prefix="!", help_command=None)


@bot.event
async def on_ready():
    print("봇이 시작되었습니다.")


@bot.command(aliases=["안녕", "ㅎㅇ", "인사"])
async def Hello(ctx):
    await ctx.send("{} 반갑습니다.".format(ctx.author.mention))

    
@bot.command(aliases=["help"])
async def 도움(ctx):
    help_ = """
픽창 예시 : 
Hide on bush님이 로비에 참가하셨습니다.
강자석님이 로비에 참가하셨습니다.
모하쉔님이 로비에 참가하셨습니다.
고수달님이 로비에 참가하셨습니다.
암살럭스님이 로비에 참가하셨습니다.


!Hello, !안녕, !ㅎㅇ, !인사 : 인사를 해줍니다.
!total, !전체승률, !승률 (소환사명 혹은 픽창에서 드래그) : 각 소환사별 전체 승률
!kda, !킬뎃, !킬데스 (소환사명 혹은 픽창에서 드래그) : 각 소환사별 최근 10판 kda
!recent_win, !최근, !최근전적, !열판 : 각 소환사별 최근 10판 승률
!every, !all, !모두, !전부 : 각 소환사별 위 셋 정보
!dodge, !닷지 : !every 에 나오는 모든 정보와 이번 게임에서의 승률, 닷지 추천
    """
    await ctx.send(help_)
    
    
@bot.command(aliases=["전체승률", "승률"])
async def total(ctx, *, msg):
    summoner_ids = []
    summoner_tot_winrates = []
    summonername_lobby = msg.split("\n")
    summonernames = nickname_separator(summonername_lobby)
    for q in summonernames:
        summoner_id, summoner_puuid = encrypt_id(api_key, q)
        summoner_ids.append(summoner_id)
    for w in summoner_ids:
        summoner_tot_winrate = total_winrate(api_key, w)
        summoner_tot_winrates.append(summoner_tot_winrate)
    out = "소환사명 | 전체승률\n"
    for (a, b) in zip(summonernames, summoner_tot_winrates):
        out += "{} | {}\n".format(a, b)
    await ctx.send(out)


@bot.command(aliases=["킬뎃", "킬데스"])
async def kda(ctx, *, msg):
    summoner_ids = []
    summoner_puuids = []
    summoner_matches = []
    match_winrates = []
    match_kdas = []
    summonername_lobby = msg.split("\n")
    summonernames = nickname_separator(summonername_lobby)
    for q in summonernames:
        summoner_id, summoner_puuid = encrypt_id(api_key, q)
        summoner_ids.append(summoner_id)
        summoner_puuids.append(summoner_puuid)
    for e in summoner_puuids:
        summoner_match = match_encrypted(api_key, e)
        summoner_matches.append(summoner_match)
    for (r, t) in zip(summoner_matches, summoner_ids):
        match_winrate, match_kda = recent_match_info(api_key, r, t)
        match_winrates.append(match_winrate)
        match_kdas.append(match_kda)
    out = "소환사명 | 최근KDA(최대 10판)\n"
    for (a, b) in zip(summonernames, match_kdas):
        out += "{} | {}\n".format(a, b)
    await ctx.send(out)


@bot.command(aliases=["최근", "최근전적", "10판"])
async def recent_win(ctx, *, msg):
    summoner_ids = []
    summoner_puuids = []
    summoner_matches = []
    match_winrates = []
    match_kdas = []
    summonername_lobby = msg.split("\n")
    summonernames = nickname_separator(summonername_lobby)
    for q in summonernames:
        summoner_id, summoner_puuid = encrypt_id(api_key, q)
        summoner_ids.append(summoner_id)
        summoner_puuids.append(summoner_puuid)
    for e in summoner_puuids:
        summoner_match = match_encrypted(api_key, e)
        summoner_matches.append(summoner_match)
    for (r, t) in zip(summoner_matches, summoner_ids):
        match_winrate, match_kda = recent_match_info(api_key, r, t)
        match_winrates.append(match_winrate)
        match_kdas.append(match_kda)
    out = "소환사명 | 최근승률(최대 10판)\n"
    for (a, b) in zip(summonernames, match_winrates):
        out += "{} | {}\n".format(a, b)
    await ctx.send(out)


@bot.command(aliases=["all", "모두", "전부"])
async def every(ctx, *, msg):
    summoner_ids = []
    summoner_puuids = []
    summoner_tot_winrates = []
    summoner_matches = []
    match_winrates = []
    match_kdas = []
    summonername_lobby = msg.split("\n")
    summonernames = nickname_separator(summonername_lobby)
    for q in summonernames:
        summoner_id, summoner_puuid = encrypt_id(api_key, q)
        summoner_ids.append(summoner_id)
        summoner_puuids.append(summoner_puuid)
    for w in summoner_ids:
        summoner_tot_winrate = total_winrate(api_key, w)
        summoner_tot_winrates.append(summoner_tot_winrate)
    for e in summoner_puuids:
        summoner_match = match_encrypted(api_key, e)
        summoner_matches.append(summoner_match)
    for (r, t) in zip(summoner_matches, summoner_ids):
        match_winrate, match_kda = recent_match_info(api_key, r, t)
        match_winrates.append(match_winrate)
        match_kdas.append(match_kda)
    out = "소환사명 | 전체승률\n"
    for (a, b) in zip(summonernames, summoner_tot_winrates):
        out += "{} | {}\n".format(a, b)
    out += "\n소환사명 | 최근승률(최대 10판)\n"
    for (c, d) in zip(summonernames, match_winrates):
        out += "{} | {}\n".format(c, d)
    out += "\n소환사명 | 최근KDA(최대 10판)\n"
    for (e, f) in zip(summonernames, match_kdas):
        out += "{} | {}\n".format(e, f)
    await ctx.send(out)


@bot.command(aliases=["닷지"])
async def dodge(ctx, *, msg):
    summoner_ids = []
    summoner_puuids = []
    summoner_tot_winrates = []
    summoner_matches = []
    match_winrates = []
    match_kdas = []
    summonername_lobby = msg.split("\n")
    summonernames = nickname_separator(summonername_lobby)
    for q in summonernames:
        summoner_id, summoner_puuid = encrypt_id(api_key, q)
        summoner_ids.append(summoner_id)
        summoner_puuids.append(summoner_puuid)
    for w in summoner_ids:
        summoner_tot_winrate = total_winrate(api_key, w)
        summoner_tot_winrates.append(summoner_tot_winrate)
    for e in summoner_puuids:
        summoner_match = match_encrypted(api_key, e)
        summoner_matches.append(summoner_match)
    for (r, t) in zip(summoner_matches, summoner_ids):
        match_winrate, match_kda = recent_match_info(api_key, r, t)
        match_winrates.append(match_winrate)
        match_kdas.append(match_kda)
    match_kdas_to_winrate = kda_score_translator(match_kdas)
    dodge_info = dodge_calculator(summoner_tot_winrates, match_kdas_to_winrate, match_winrates)
    out = "소환사명 | 전체승률\n"
    for (a, b) in zip(summonernames, summoner_tot_winrates):
        out += "{} | {}\n".format(a, b)
    out += "\n소환사명 | 최근승률(최대 10판)\n"
    for (c, d) in zip(summonernames, match_winrates):
        out += "{} | {}\n".format(c, d)
    out += "\n소환사명 | 최근KDA(최대 10판)\n"
    for (e, f) in zip(summonernames, match_kdas):
        out += "{} | {}\n".format(e, f)
    if dodge_info < 50:
        out += "\n닷지를 추천드립니다. 승률: {}".format(dodge_info)
    else:
        out += "\n승률이 50퍼센트 이상입니다. 승률: {}".format(dodge_info)
    await ctx.send(out)



access_token = os.environ['BOT_TOKEN']
bot.run(access_token)

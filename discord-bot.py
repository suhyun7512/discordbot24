import discord
import os
from discord.ext import commands
import firebase_admin
from firebase_admin import credentials, firestore
from discord.ui import Button, View
import asyncio
import random
from decimal import Decimal, getcontext
import copy



# 정확도를 높여 부동소수점 연산의 오차를 최소화
getcontext().prec = 6

# 공격속도를 Decimal로 선언
attack_speed = Decimal('0.3')

# Firebase 서비스 계정 키(JSON) 파일명
cred_filename = 'discordbot-2bc59-firebase-adminsdk-3gwj5-d01bdc45e1.json'

# Firebase 초기화
cred = credentials.Certificate(cred_filename)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://discordbot-2bc59-default-rtdb.firebaseio.com'
})

# Firestore 데이터베이스 초기화
db = firestore.client()

# 인텐트 설정
intents = discord.Intents.all()
intents.messages = True

# 봇 생성C
bot = commands.Bot(command_prefix='희루야 ', intents=intents)

# 봇이 준비되면 실행되는 이벤트
@bot.event
async def on_ready():
    print(f'봇이 성공적으로 로그인했습니다: {bot.user.name}')
    await bot.change_presence(status=discord.Status.online)
    await bot.change_presence(activity=discord.Game(name="희루랑 친해질려면 - 희루야 명령어"))



@bot.command(name='몬스터목록', aliases=['몬스터', '목록'])
async def show_monster_list(ctx):
    monster_names = list(monster_data.keys())

    embed = discord.Embed(
        title="몬스터 목록",
        color=discord.Color.blue()
    )
    embed.add_field(name="몬스터 이름", value='\n'.join(monster_names), inline=False)

    await ctx.send(embed=embed)
    await ctx.send('몬스터 상세정보는 "희루야 몬스터상세 [이름]"으로 확인하세요.')


@bot.command(name='몬스터상세')
async def show_monster_detail(ctx, monster_name):
    monster_name = monster_name.lower()

    if monster_name in monster_data:
        monster_info = monster_data[monster_name]

        embed = discord.Embed(
            title=f"{monster_name} 몬스터 상세 정보",
            color=discord.Color.green()
        )
        for stat, value in monster_info.items():
            embed.add_field(name=stat, value=value, inline=False)

        await ctx.send(embed=embed)
    else:
        await ctx.send(f"{monster_name} 몬스터를 찾을 수 없습니다.")

@bot.command(name='명령어')
async def command_list(ctx):
    # Embed 생성
    embed = discord.Embed(
        title="📑 희루봇 명령어",
        description="희루봇을 이용할수 있는 명령어들입니다~!",
        color=discord.Color.blue()
    )

    # 각 명령어에 대한 설명 추가
    embed.add_field(name="대화", value="`희루야 대화 [대화내용]` - 희루봇과 대화가 가능합니다.", inline=False)
    embed.add_field(name="희루봇 가르치기", value="`희루야 배워 [배울단어] [응답할 내용]` - 희루봇을 가르치는 선생님이 됩니다!", inline=False)
    embed.add_field(name="캐릭터 생성", value="`희루야 캐릭터생성 [이름]` - 캐릭터를 생성합니다.", inline=False)
    embed.add_field(name="캐릭터 정보", value="`희루야 정보` - 현재 캐릭터의 정보를 확인합니다.", inline=False)
    embed.add_field(name="몬스터 목록", value="`희루야 몬스터목록` - 현재 등장하는 몬스터들을 확인합니다.", inline=False)
    embed.add_field(name="몬스터 상세 정보", value="`희루야 몬스터상세 [이름]` - 특정 몬스터의 상세 정보를 확인합니다.", inline=False)
    embed.add_field(name="캐릭터 상점", value="`희루야 상점` - 상점 이용이 가능합니다.", inline=False)
    embed.add_field(name="캐릭터 장비구매", value="`희루야 구매 [아이템명]` - 구매가 가능합니다.", inline=False)
    embed.add_field(name="캐릭터 사냥", value="`희루야 사냥 [몬스터 이름]` - 사냥이 가능합니다.", inline=False)
    embed.add_field(name="던전입장", value="`희루야 던전입장` - 희루의 던전이 가능합니다.", inline=False)

    embed.add_field(name="명령어", value="`희루야 명령어` - 사용 가능한 명령어들을 확인합니다.", inline=False)

    # Embed 전송
    await ctx.send(embed=embed)

# "대화하자"라는 메시지에 대한 응답
@bot.command(name='대화하자')
async def initiate_conversation(ctx):
    # 해당 채널의 ID를 Firebase에 저장
    channel_id = ctx.channel.id
    doc_ref = db.collection('channels').document(str(channel_id))
    doc_ref.set({
        'channel_id': channel_id
    })
    await ctx.send('이 채널에서 희루봇 명령어를 사용할 수 있습니다.')

# "희루야 캐릭터생성" 명령어
@bot.command(name='캐릭터생성')
async def create_character(ctx, *, name):  # name을 인자로 받도록 수정
    # 캐릭터 정보를 Firestore에 저장
    user_id = str(ctx.author.id)
    doc_ref = db.collection('characters').document(user_id)
    
    # 이미 해당 유저의 캐릭터가 있는지 확인
    existing_doc = doc_ref.get()
    if existing_doc.exists:
        await ctx.send('이미 캐릭터가 존재합니다.')
    else:
        doc_ref.set({
            'name': name,
            'level': 1,
            'hp': 100,
            'attack': 5,
            'defense': 5,
            'exp': 0,
            'attack_speed': 0.2,
            'gold': 100  # 'gold' 키를 추가하고 초기값으로 100 설정
        })
        await ctx.send(f'{name} 캐릭터가 생성되었습니다.')

shop_items = {
    '롱소드': {'가격': 100, '능력치': {'공격력': 25}, '이모지': '🗡'},
    '방어구': {'가격': 30, '능력치': {'방어력': 15}, '이모지': '🛡'},
    '수정': {'가격': 10, '능력치': {'HP': 50}, '이모지': '💎'},
    '석궁': {'가격':200,'능력치':{'공격속도':5},'이모지': '🏹'},
    '글러브': {'가격':1000,'능력치':{'공격력':60},'이모지':'🥊'},
    '강화심장': {'가격':2000,'능력치':{'HP':200},'이모지':'💝'},
    '안전모자': {'가격':20000,'능력치':{'방어력':50,'HP':200},'이모지':'⛑'},
    '쌍검': {'가격':25000,'능력치':{'공격속도':5,'공격력':50},'이모지':'⚔️'},
    '도끼': {'가격':45000,'능력치':{'HP':250,'공격력':75},'이모지':'🪓'}
}

# "희루야 상점" 명령어
@bot.command(name='상점')
async def shop(ctx):
    # 캐릭터 정보 조회
    user_id = str(ctx.author.id)
    doc_ref = db.collection('characters').document(user_id)
    doc = doc_ref.get()

    if doc.exists:
        character_data = doc.to_dict()

        # 상점에서 판매할 아이템 목록 (간단한 예시)
        shop_items = {
            '롱소드': {'가격': 100, '능력치': {'공격력': 25}, '이모지': '🗡'},
            '방어구': {'가격': 30, '능력치': {'방어력': 15}, '이모지': '🛡'},
            '수정': {'가격': 10, '능력치': {'HP': 50}, '이모지': '💎'},
            '석궁': {'가격':200,'능력치':{'공격속도':5},'이모지': '🏹'},
            '글러브': {'가격':1000,'능력치':{'공격력':60},'이모지':'🥊'},
            '강화심장': {'가격':2000,'능력치':{'HP':200},'이모지':'💝'},
            '안전모자': {'가격':20000,'능력치':{'방어력':50,'HP':200},'이모지':'⛑'},
            '쌍검': {'가격':25000,'능력치':{'공격속도':5,'공격력':50},'이모지':'⚔️'},
            '도끼': {'가격':45000,'능력치':{'HP':250,'공격력':75},'이모지':'🪓'}
        }

        # Embed 생성
        embed = discord.Embed(
            title="🛒 상점",
            description="상점에서 구매할 수 있는 아이템 목록",
            color=discord.Color.gold()
        )

        for item, data in shop_items.items():
            # 능력치를 '능력명 +값' 형식으로 표시
            stat_str = ', '.join([f'{stat} +{value}' for stat, value in data["능력치"].items()])
            embed.add_field(name=f'{data["이모지"]} {item} - {data["가격"]}원', value=stat_str, inline=False)

        await ctx.send(embed=embed)
        await ctx.send('구매하려면 "희루야 구매 [아이템명]"을 입력하세요.')
    else:
        await ctx.send('아직 캐릭터를 생성하지 않았습니다. `희루야 캐릭터생성 [이름]`으로 캐릭터를 생성해주세요.')

# "희루야 구매" 명령어
@bot.command(name='구매')
async def buy_item(ctx, item_name):
    # 캐릭터 정보 조회
    user_id = str(ctx.author.id)
    doc_ref = db.collection('characters').document(user_id)
    doc = doc_ref.get()

    if doc.exists:
        character_data = doc.to_dict()

        # 입력받은 아이템명을 소문자로 변환하여 사용
        item_name = item_name.lower()

        # "장비" 키가 없는 경우 초기화
        if "장비" not in character_data:
            character_data["장비"] = {}

        if item_name in shop_items:
            # 이미 소지한 아이템인지 확인
            if item_name in character_data["장비"]:
                await ctx.send('이미 소지한 아이템은 구매할 수 없습니다.')
                return

            # 선택된 아이템 구매 처리
            price = shop_items[item_name]["가격"]
            if character_data["gold"] >= price:
                # 돈이 충분한 경우 아이템을 캐릭터에게 적용하고 돈 차감
                character_data["gold"] -= price

                # 아이템 추가
                character_data["장비"][item_name] = shop_items[item_name]["능력치"]

                # 능력치 적용
                for stat, value in shop_items[item_name]["능력치"].items():
                    if stat == '공격력':
                        character_data['attack'] += value
                    elif stat == '방어력':
                        character_data['defense'] += value
                    elif stat == 'HP':
                        character_data['hp'] += value
                    elif stat == '공격속도': 
                        character_data['attack_speed'] += value

                # 캐릭터 정보 업데이트
                doc_ref.update(character_data)

                await ctx.send(f'{shop_items[item_name]["이모지"]} {item_name}를 구매하였습니다. 남은 돈: {character_data["gold"]}')
            else:
                await ctx.send('돈이 부족하여 구매할 수 없습니다.')
        else:
            await ctx.send(f'{item_name}은(는) 상점에 존재하지 않는 아이템입니다.')
    else:
        await ctx.send('아직 캐릭터를 생성하지 않았습니다. `희루야 캐릭터생성 [이름]`으로 캐릭터를 생성해주세요.')

# 레벨별 필요 경험치 계산 함수 추가
def calculate_exp_required(level):
    return level * 15 + 100

# 레벨업 함수 수정
async def level_up(ctx, character_data):
    # 현재 레벨과 경험치
    current_level = character_data['level']
    current_exp = character_data['exp']

    # 레벨업 필요 경험치 계산
    exp_required = calculate_exp_required(current_level)

    # 레벨업 조건 확인
    if current_exp >= exp_required:
        # 레벨 업
        character_data['level'] += 1
        character_data['exp'] -= exp_required  # 레벨업 후 경험치 차감

        # 레벨업에 따른 스탯 상승
        character_data['hp'] += 5
        character_data['attack'] += 4
        character_data['defense'] += 2
        character_data['gold'] += 200

        # 업데이트된 정보를 Firestore에 저장
        user_id = str(ctx.author.id)
        doc_ref = db.collection('characters').document(user_id)
        doc_ref.update(character_data)

        await ctx.send(f"🎉 축하합니다! {character_data['name']}님,🌟 레벨이 {current_level + 1}로 상승했습니다!"
                       f"\n📈 레벨업 보상: 💗 HP +5, 🗡 공격력 +4, 🛡 방어력 +2, 💰 골드 +200")
        
        if current_exp >= exp_required:
            await level_up(ctx, character_data)

# 몬스터 데이터
monster_data = {
    '슬라임': {'체력': 50, '공격력': 7, '🛡 방어력': 2, '🏹 공격속도': 0.5, '경험치': 25, '골드': 15},
    '고블린': {'체력': 100, '공격력': 15, '🛡 방어력': 12, '🏹 공격속도': 1.0, '경험치': 35, '골드': 27},
    '좀비': {'체력': 150, '공격력': 18, '🛡 방어력': 17, '🏹 공격속도': 1.1, '경험치': 45, '골드': 34},
    '오크': {'체력': 250, '공격력': 45, '🛡 방어력': 19, '🏹 공격속도': 1.3, '경험치': 75, '골드': 48},
    '마법사': {'체력': 350, '공격력': 52, '🛡 방어력': 20, '🏹 공격속도': 1.5, '경험치': 95, '골드': 72},
    '마녀': {'체력': 400, '공격력': 70, '🛡 방어력': 24, '🏹 공격속도': 1.7, '경험치': 125, '골드': 80},
    '드래곤': {'체력': 500, '공격력': 85, '🛡 방어력': 32, '🏹 공격속도': 2.0, '경험치': 185, '골드': 102},
    '유령': {'체력': 1000, '공격력': 125, '🛡 방어력': 42, '🏹 공격속도': 2.4, '경험치': 245, '골드': 155}
}

# get_monster_info 함수 추가
def get_monster_info(monster_name):
    monsters = {
        '슬라임': {'체력': 50, '공격력': 7, '🛡 방어력': 2, '🏹 공격속도': 0.5, '경험치': 25, '골드': 15},
        '고블린': {'체력': 100, '공격력': 15, '🛡 방어력': 12, '🏹 공격속도': 1.0, '경험치': 35, '골드': 27},
        '좀비': {'체력': 150, '공격력': 18, '🛡 방어력': 17, '🏹 공격속도': 1.1, '경험치': 45, '골드': 34},
        '오크': {'체력': 250, '공격력': 45, '🛡 방어력': 19, '🏹 공격속도': 1.3, '경험치': 75, '골드': 48},
        '마법사': {'체력': 350, '공격력': 52, '🛡 방어력': 20, '🏹 공격속도': 1.5, '경험치': 95, '골드': 72},
        '마녀': {'체력': 400, '공격력': 70, '🛡 방어력': 24, '🏹 공격속도': 1.7, '경험치': 125, '골드': 80},
        '드래곤': {'체력': 500, '공격력': 85, '🛡 방어력': 32, '🏹 공격속도': 2.0, '경험치': 185, '골드': 102},
        '유령': {'체력': 1000, '공격력': 125, '🛡 방어력': 42, '🏹 공격속도': 2.4, '경험치': 245, '골드': 155}
    }

    return monsters.get(monster_name)

# get_monster_info 함수 수정
def get_monster_info(monster_name):
    monster_info = monster_data.get(monster_name)
    if monster_info:
        monster_info['name'] = monster_name  # 몬스터 정보에 이름 추가
    return monster_info

# 사냥 명령어 수정
@bot.command(name='사냥')
async def start_battle(ctx, *, monster_name):
    # 캐릭터 정보를 Firestore에서 가져오기
    user_id = str(ctx.author.id)
    doc_ref = db.collection('characters').document(user_id)
    character_data = doc_ref.get().to_dict()

    # 몬스터 정보 가져오기
    monster_info = get_monster_info(monster_name)

    # 전투 시작
    if monster_info:
        await battle(ctx, character_data, monster_info, monster_name)
    else:
        await ctx.send(f"{monster_name} 몬스터를 찾을 수 없습니다.")

# 전투 함수 수정
async def battle(ctx, character_data, monster_info, monster_name):
    # 전투 중인 메시지 생성
    battle_embed = discord.Embed(title=f"{monster_name}과 전투 중", color=discord.Color.green())
    battle_embed.add_field(name=f"🗡 {character_data['name']}의 공격", value="전투가 시작됩니다.", inline=False)

    # 전투 중인 메시지 전송
    battle_msg = await ctx.send(embed=battle_embed)

    # 플레이어와 몬스터의 체력
    player_hp = character_data["hp"]
    monster_hp = monster_info["체력"]

    # 전투 라운드 반복
    round_num = 1
    while player_hp > 0 and monster_hp > 0:
        # 플레이어 공격
        player_attack = character_data["attack"]
        monster_hp -= player_attack

        # 몬스터가 살아있으면 몬스터의 공격
        if monster_hp > 0:
            monster_attack = monster_info["공격력"]
            if monster_attack > character_data["defense"]:
                monster_attack -= character_data["defense"]
            else:
                monster_attack = 0
            player_hp -= monster_attack

            # 이전 라운드의 로그 삭제
            if round_num >= 2:
                battle_embed.clear_fields()  # 모든 필드 삭제

            # 전투 중인 메시지 수정
            battle_embed.set_footer(text=f"라운드 {round_num}")
            battle_embed.add_field(name=f"🗡 {character_data['name']}의 공격", value=f"{monster_name}에게 -{player_attack}의 피해 (남은 💗 HP: {monster_hp})", inline=False)
            battle_embed.add_field(name="🛡 몬스터의 공격", value=f"{character_data['name']}는 -{monster_attack}의 피해를 입었습니다. (남은 💗 HP: {player_hp})", inline=False)
            await battle_msg.edit(embed=battle_embed)

            # 다음 라운드로
            round_num += 1
            await asyncio.sleep(0.5)  # 간격 조절

    # 전투 종료 후 결과 처리
    await battle_end(ctx, player_hp, monster_hp, monster_info)

# 전투 종료 함수 수정
async def battle_end(ctx, player_hp, monster_hp, monster_info):
    # 이전 메시지 수정
    async for message in ctx.history(limit=10):  # 최근 10개의 메시지 확인
        if message.author.id == bot.user.id and message.embeds:
            embed = message.embeds[0]  # 첫 번째 Embed 가져오기
            embed.clear_fields()  # 기존 필드 모두 삭제

            if player_hp <= 0:
                await asyncio.sleep(2)
                embed.title = "전투 결과 - 패배"
                embed.color = discord.Color.red()  # 패배일 때는 빨간색으로 변경
                embed.description = f"{monster_info.get('name', 'Unknown Monster')} 몬스터에게 패배했습니다."
            else:
                # 경험치 및 골드 획득
                exp_gain = monster_info.get("경험치", 0)
                gold_gain = monster_info.get("골드", 0)

                # 플레이어에게 경험치 및 골드 추가
                user_id = str(ctx.author.id)
                doc_ref = db.collection('characters').document(user_id)
                character_data = doc_ref.get().to_dict()

                # 경험치와 골드를 캐릭터에 추가
                character_data['exp'] += exp_gain
                character_data['gold'] += gold_gain

                # 업데이트된 정보를 Firestore에 저장
                doc_ref.update(character_data)

                embed.title = f"전투 결과 - 승리"
                embed.color = discord.Color.blue()  # 승리일 때는 파란색으로 변경
                embed.description = f"{monster_info['name']} 몬스터를 처치하여 보상을 얻었습니다. \n\n보상목록:\n✨ 경험치: +{exp_gain} \n💰 골드: +{gold_gain}"

                await level_up(ctx, character_data)

            await message.edit(embed=embed)
            break

# 학습된 명령어와 응답을 가져오는 함수
def get_learned_response_from_firebase(command):
    ref = ref = db.collection('learned_commands')
    data = ref.get()
    if data and command in data:
        return data[command]
    return None

@bot.command(name='대화')
async def chat(ctx, command: str):
    # Firestore 컬렉션 참조
    ref = db.collection('learned_commands').document('global')

    # 문서 가져오기
    doc = ref.get()

    # 문서가 존재하면 명령어와 응답 출력
    if doc.exists:
        data = doc.to_dict()
        response = data.get(command)
        if response:
            await ctx.send(response)
        else:
            await ctx.send(f'"{command}" 아직 희루는 못 배운 단어에요!')
    else:
        await ctx.send('띠용??')

@bot.command(name='배워')
async def learn_command(ctx, command: str, *, response: str):
    # Firestore 컬렉션 참조
    ref = db.collection('learned_commands').document('global')

    # 문서 가져오기
    doc = ref.get()

    # 문서가 존재하면 명령어와 응답을 업데이트
    if doc.exists:
        data = doc.to_dict()
        
        # 이미 배운 명령어인 경우 수정 불가능하도록 처리
        if command in data:
            await ctx.send(f'"{command}" 는 이미 배웠어요...')
        else:
            data[command] = response
            ref.update(data)
            await ctx.send(f'"{command}" 라는 단어를 배웠어요!!')
    else:
        # 문서가 없으면 새로운 문서 생성
        ref.set({command: response})
        await ctx.send(f'"{command}" 라는 단어를 배웠어요!!')

dungeon_data = {
    'floor': 1,
    'test': 1,
    'Dungeon_Confirmed':0,
    'Gold_Reward':0,
    'monsters': {},
    'Experience':0,
    'last_clear':0,
}

player_hp = None
dungeon_log = []
dungeon_enter = 0
dungeon_entry_status = {}

@bot.command(name='던전입장')
async def enter_dungeon(ctx):
    user_id = str(ctx.author.id)

    # 이미 다른 사용자가 던전에 입장한 경우
    if any(entry_status for entry_status in dungeon_entry_status.values()):
        await ctx.send('이미 누군가 던전에 진입했습니다!')
        return

    # 이미 현재 사용자가 던전에 입장한 경우
    if dungeon_entry_status.get(user_id, False):
        await ctx.send('이미 던전에 진입했습니다!')
        return

    doc_ref = db.collection('characters').document(user_id)
    character_data = doc_ref.get().to_dict()

    if character_data['level'] >= 20:
        global player_hp, dungeon_log, battle_log

        # 던전에 입장 중으로 표시
        dungeon_entry_status[user_id] = True

        # 사용자 정보 초기화
        player_hp = character_data['hp']
        dungeon_log = []
        dungeon_data['Gold_Reward'] = 0
        dungeon_data['Experience'] = 0
        dungeon_data['floor'] = 1
        dungeon_data['last_clear'] = 0

        await ctx.send(embed=await create_dungeon_embed(dungeon_data, player_hp, dungeon_log))

        await dungeon_start(ctx, player_hp, dungeon_log)
    else:
        await ctx.send('희루 던전은 20렙 이상만 가능합니다!')

        # 던전 입장 여부를 다시 False로 설정
        dungeon_entry_status[user_id] = False

async def dungeon_start(ctx, player_hp, dungeon_log):
    async for message in ctx.channel.history(limit=3):
        if message.author == bot.user and message.embeds:
            await message.edit(embed=await create_dungeon_embed(dungeon_data, player_hp, dungeon_log))
            break
    else:
        await ctx.send(embed=await create_dungeon_embed(dungeon_data, player_hp, dungeon_log))

    if dungeon_data['Dungeon_Confirmed'] > 6:
        dungeon_data['Dungeon_Confirmed'] = 0
        event = random.choices(['이동'], weights=[1])[0]
    else:
        if dungeon_data['floor'] == 7:
            event = random.choices(['몬스터'], weights=[1])[0]
        else:
            event = random.choices(['몬스터', '상자', '함정', '이동'], weights=[0.5, 0.3, 0.1, 0.1])[0]

    if event == '몬스터':
        await dungeon_moster(ctx, player_hp, dungeon_log)
    elif event == '상자':
        await open_box(ctx, player_hp, dungeon_log)
    elif event == '함정':
        await dungeom_trap(ctx, player_hp, dungeon_log)
    elif event == '이동':
        await move_to_next_floor(ctx, player_hp, dungeon_log)

async def create_dungeon_embed(dungeon_data, player_hp, dungeon_log):
    dungeon_embed = discord.Embed(
        title=f"희루의 던전 - 지하 {dungeon_data['floor']}층",
        color=discord.Color.gold()
    )

    dungeon_embed.description = f"매우 음산한 분위기이다.."

    dungeon_embed.add_field(name="💗 현재 체력:", value=f"{player_hp}", inline=False)

    dungeon_embed.add_field(name="탐험 기록", value="\n".join(dungeon_log), inline=False)

    return dungeon_embed

async def open_box(ctx, player_hp, dungeon_log):
    # await ctx.send("상자 발견!!")
    dungeon_log.append(f"🔎 상자 발견!")

    open_box = random.choices(['함정', '보상','힐'], weights=[0.25, 0.45, 0.3])[0]
    if open_box == '함정':
        # await ctx.send(f"앗 상자는 함정이였다..!! 💗 현재 체력: {player_hp-10}")

        dungeon_log.append(f"💣상자는 함정이였습니다.. 💗 체력: -10")
        dungeon_data['Dungeon_Confirmed'] +=1

        if player_hp <= 0:
            await asyncio.sleep(2)
            await dungeon_fail(ctx)
            return

        player_hp -=10

        await dungeon_start(ctx, player_hp, dungeon_log)
    elif open_box == '보상':
        user_id = str(ctx.author.id)
        doc_ref = db.collection('characters').document(user_id)
        character_data = doc_ref.get().to_dict()

        # await ctx.send(f"보상이 가득한 상자였습니다!")
        earned_gold = random.randint(100, 1000)
        dungeon_data['Gold_Reward'] += earned_gold

        dungeon_log.append(f"🎉 상자에서 {earned_gold}만큼의 골드를 얻었습니다")
        dungeon_data['Dungeon_Confirmed'] +=1

        await dungeon_start(ctx, player_hp, dungeon_log)

    elif open_box == '힐':
        # await ctx.send(f"치유의 상자였습니다! 💗 현재 체력: {player_hp+20}")

        dungeon_log.append(f"🩹치료 완료! 💗 체력: +20")
        dungeon_data['Dungeon_Confirmed'] +=1

        player_hp +=20

        await dungeon_start(ctx, player_hp, dungeon_log)

async def dungeom_trap(ctx, player_hp, dungeon_log):
    # await ctx.send(f"앗 함정에 당했다..!! 💗 현재 체력: {player_hp-10}")
    
    dungeon_log.append(f"함정에 걸렸습니다. 💗 체력: -10")
    dungeon_data['Dungeon_Confirmed'] +=1

    if player_hp <= 0:
        await asyncio.sleep(2)
        await dungeon_fail(ctx)
        return

    player_hp -=10
    await dungeon_start(ctx, player_hp, dungeon_log)

async def move_to_next_floor(ctx, player_hp, dungeon_log):
    global dungeon_data 

    dungeon_log.clear()

    dungeon_log = []

    dungeon_log.append(f"지하 {dungeon_data['floor']+1}층으로 내려간다..")

    dungeon_data['floor'] += 1
    await dungeon_start(ctx, player_hp, copy.deepcopy(dungeon_log))

async def clear_dungeon(ctx):
    user_id = str(ctx.author.id)
    doc_ref = db.collection('characters').document(user_id)
    character_data = doc_ref.get().to_dict()
    
    clear_embed = discord.Embed(
        title="보상 목록",
        color=discord.Color.gold()
    )
    clear_embed.description = f"던전 클리어 보상- \n\n보상목록:\n✨ 경험치: + {(dungeon_data['Experience']+2500)*2} \n💰 골드: + {(dungeon_data['Gold_Reward']+2500)*2}"
    await ctx.send(embed=clear_embed)

    character_data['gold'] +=  dungeon_data['Gold_Reward']
    character_data['exp'] +=  dungeon_data['Experience']

    character_data['exp'] += 2500
    character_data['gold'] += 1000

    dungeon_entry_status[user_id] = False

    await level_up(ctx, character_data)

async def dungeon_fail(ctx):
    global dungeon_enter, battle_msg

    user_id = str(ctx.author.id)
    doc_ref = db.collection('characters').document(user_id)
    character_data = doc_ref.get().to_dict()

    await battle_msg.delete()

    fail_embed = discord.Embed(
        title="희루 던전 실패..",
        color=discord.Color.red()
    )
    fail_embed.description = "더 강해지셔서 오세요!!"
    fail_embed.description = f"그동안 찾은 보상은 드리죠. \n\n✨ 경험치: + {dungeon_data['Experience']} \n💰 골드: + {dungeon_data['Gold_Reward']}"
    character_data['gold'] +=  dungeon_data['Gold_Reward']
    character_data['exp'] +=  dungeon_data['Experience']
    dungeon_enter = 0
    dungeon_entry_status[user_id] = False
    await ctx.send(embed=fail_embed)


dungeon_monster_data = {
    '슬라임': {'체력': 50, '공격력': 7, '🛡 방어력': 7, '🏹 공격속도': 0.2, '경험치': 15, '골드': 8},
    '고블린': {'체력': 70, '공격력': 9, '🛡 방어력': 12, '🏹 공격속도': 0.2, '경험치': 25, '골드': 17},
    '스켈레톤': {'체력': 80, '공격력': 10, '🛡 방어력': 8, '🏹 공격속도': 0.2, '경험치': 20, '골드': 12},
    '푸른버섯': {'체력': 60, '공격력': 8, '🛡 방어력': 5, '🏹 공격속도': 0.2, '경험치': 18, '골드': 10},

    '오크': {'체력': 250, '공격력': 155, '🛡 방어력': 19, '🏹 공격속도': 0.5, '경험치': 55, '골드': 28},
    '어스름늑대': {'체력': 220, '공격력': 80, '🛡 방어력': 15, '🏹 공격속도': 0.7, '경험치': 70, '골드': 20},
    '두꺼비': {'체력': 240, '공격력': 75, '🛡 방어력': 10, '🏹 공격속도': 0.4, '경험치': 65, '골드': 15},
    '좀비': {'체력': 250, '공격력': 98, '🛡 방어력': 17, '🏹 공격속도': 0.5, '경험치': 75, '골드': 21},
    '마법사': {'체력': 250, '공격력': 172, '🛡 방어력': 20, '🏹 공격속도': 0.4, '경험치': 65, '골드': 32},
    
    '마녀': {'체력': 800, '공격력': 270, '🛡 방어력': 84, '🏹 공격속도': 1.1, '경험치': 105, '골드': 40},
    '전령': {'체력': 900, '공격력': 240, '🛡 방어력': 125, '🏹 공격속도': 0.9, '경험치': 240, '골드': 50},
    '미믹': {'체력': 1000, '공격력': 110, '🛡 방어력': 200, '🏹 공격속도': 0.8, '경험치': 150, '골드': 25},
    '드래곤': {'체력': 1000, '공격력': 305, '🛡 방어력': 102, '🏹 공격속도': 1.5, '경험치': 175, '골드': 52},

    '유령': {'체력': 1500, '공격력': 455, '🛡 방어력': 222, '🏹 공격속도': 1.7, '경험치': 305, '골드': 75},
    '거인': {'체력': 2100, '공격력': 730, '🛡 방어력': 425, '🏹 공격속도': 1.1, '경험치': 450, '골드': 70},
    '신수': {'체력': 1700, '공격력': 545, '🛡 방어력': 310, '🏹 공격속도': 1.5, '경험치': 300, '골드': 75},
    '반신반인': {'체력': 1650, '공격력': 640, '🛡 방어력': 270, '🏹 공격속도': 1.7, '경험치': 375, '골드': 70},

    '악마': {'체력': 1800, '공격력': 665, '🛡 방어력': 415, '🏹 공격속도': 2.4, '경험치': 700, '골드': 505},
    '용사': {'체력': 2400, '공격력': 775, '🛡 방어력': 520, '🏹 공격속도': 2.4, '경험치': 800, '골드': 605},
    '요정': {'체력': 2000, '공격력': 480, '🛡 방어력': 385, '🏹 공격속도': 2.1, '경험치': 850, '골드': 305}, 
    '도깨비': {'체력': 2100, '공격력': 570, '🛡 방어력': 420, '🏹 공격속도': 2.7, '경험치': 750, '골드': 270},
    
    '하피': {'체력': 3480, '공격력': 1240, '🛡 방어력': 600, '🏹 공격속도': 20.5, '경험치': 2400, '골드': 2300},
    '불의정령': {'체력': 4080, '공격력': 1700, '🛡 방어력': 670, '🏹 공격속도': 24.7, '경험치': 2700, '골드': 3800},
    '픽시': {'체력': 3700, '공격력': 1540, '🛡 방어력': 640, '🏹 공격속도': 29.5, '경험치': 2300, '골드': 2100},
    '거미여왕': {'체력': 3500, '공격력': 1320, '🛡 방어력': 580, '🏹 공격속도': 25.5, '경험치': 2500, '골드': 3000},

    '???': {'체력': 10000, '공격력': 2250, '🛡 방어력': 1550, '🏹 공격속도': 75.5, '경험치': 10500, '골드': 8500}
}

async def dungeon_moster(ctx, player_hp, dungeon_log):
    global dungeon_data, battle_log, battle_msg

    dungeon_data['Dungeon_Confirmed'] +=1

    battle_log = []

    user_id = str(ctx.author.id)
    doc_ref = db.collection('characters').document(user_id)
    character_data = doc_ref.get().to_dict()

    if dungeon_data['floor'] == 1:
        monster_types = {
            1: "슬라임",
            2: "고블린",
            3: "스켈레톤",
            4: "푸른버섯"
        }

        monster_type = random.randint(1, 4)
        monster_name = monster_types[monster_type]

        # 몬스터 정보 가져오기
        monster_info = dungeon_monster_data[monster_name]
        monster_attack_speed = monster_info['🏹 공격속도']
        monster_info = dungeon_monster_data[monster_name]
        monster_hp = monster_info['체력']
        monster_attack = monster_info['공격력']
        monster_defense = monster_info['🛡 방어력']
        monster_exp = monster_info['경험치']
        monster_gold = monster_info['골드']

        if character_data['attack_speed'] >= monster_attack_speed:
            battle_ing_embed = discord.Embed(  
                title=f"전투중 - {monster_name}",
                color=discord.Color.green()
            )
            battle_ing_embed.add_field(name="내정보", value=f"💗 체력: {player_hp}")
            battle_ing_embed.add_field(name=f"{monster_name} 정보", value=f"💗 체력: {monster_hp}")
            battle_ing_embed.add_field(name="", value="", inline=True)

            battle_msg = await ctx.send(embed=battle_ing_embed)

            battle_ing_embed.add_field(name="전투 기록", value="", inline=False)

            while player_hp > 0 and monster_hp > 0:
                battle_ing_embed.add_field(name="", value="\n".join(battle_log), inline=False)

                # 메시지 수정
                await battle_msg.edit(embed=battle_ing_embed)

                await asyncio.sleep(1)

                damage = max(0, character_data['attack'] - monster_defense) 
                monster_hp -= damage
                battle_log.append(f"🗡 {character_data['name']}의 공격! {monster_name}한테 - {damage}의 피해 (남은 💗 HP:{monster_hp})")

                await asyncio.sleep(1)
                
                await battle_msg.edit(embed=battle_ing_embed)

                if monster_hp <= 0:
                    dungeon_data['Experience'] += monster_exp
                    dungeon_data['Gold_Reward'] += monster_gold
                    await asyncio.sleep(2)
                    await dungeon_moster_clear(ctx, battle_msg, player_hp, monster_name)
                    return
                    
                await asyncio.sleep(1)

                damage = max(0, monster_attack - character_data['defense']) 
                player_hp -= damage
                battle_log.append(f"🗡 {monster_name}의 공격! {character_data['name']}한테 - {damage}의 피해 (남은 💗 HP:{player_hp})")

                await asyncio.sleep(1)
                
                await battle_msg.edit(embed=battle_ing_embed)

                if player_hp <= 0:
                    await asyncio.sleep(2)
                    await dungeon_fail(ctx)
                    return
        else:
            battle_ing_embed = discord.Embed(  
                title=f"전투중 - {monster_name}",
                color=discord.Color.green()
            )
            battle_ing_embed.add_field(name="내정보", value=f"💗 체력: {player_hp}")
            battle_ing_embed.add_field(name=f"{monster_name} 정보", value=f"💗 체력: {monster_hp}")
            battle_ing_embed.add_field(name="", value="", inline=True)

            battle_msg = await ctx.send(embed=battle_ing_embed)

            battle_ing_embed.add_field(name="전투 기록", value="", inline=False)

            while player_hp > 0 and monster_hp > 0:
                battle_ing_embed.add_field(name="", value="\n".join(battle_log), inline=False)

                # 메시지 수정
                await battle_msg.edit(embed=battle_ing_embed)

                await asyncio.sleep(1)

                damage = max(0, monster_attack - character_data['defense'])  
                player_hp -= damage
                battle_log.append(f"🗡 {monster_name}의 공격! {character_data['name']}한테 - {damage}의 피해 (남은 💗 HP:{player_hp})")

                await asyncio.sleep(1)
                
                await battle_msg.edit(embed=battle_ing_embed)

                if player_hp <= 0:
                    await asyncio.sleep(2)
                    await dungeon_fail(ctx)
                    return

                await asyncio.sleep(1)

                damage = max(0, character_data['attack'] - monster_defense) 
                monster_hp -= damage
                battle_log.append(f"🗡 {character_data['name']}의 공격! {monster_name}한테 - {damage}의 피해 (남은 💗 HP:{monster_hp})")

                await asyncio.sleep(1)
                
                await battle_msg.edit(embed=battle_ing_embed)

                if monster_hp <= 0:
                    dungeon_data['Experience'] += monster_exp
                    dungeon_data['Gold_Reward'] += monster_gold
                    await asyncio.sleep(2)
                    await dungeon_moster_clear(ctx, battle_msg, player_hp, monster_name)
                    return  
                 
    elif dungeon_data['floor'] == 2:
        monster_types = {
            1: "오크",
            2: "어스름늑대",
            3: "두꺼비",
            4: "좀비",
            5: "마법사",
        }

        monster_type = random.randint(1, 5)
        monster_name = monster_types[monster_type]

        # 몬스터 정보 가져오기
        monster_info = dungeon_monster_data[monster_name]
        monster_attack_speed = monster_info['🏹 공격속도']
        monster_info = dungeon_monster_data[monster_name]
        monster_hp = monster_info['체력']
        monster_attack = monster_info['공격력']
        monster_defense = monster_info['🛡 방어력']
        monster_exp = monster_info['경험치']
        monster_gold = monster_info['골드']

        if character_data['attack_speed'] >= monster_attack_speed:
            battle_ing_embed = discord.Embed(  
                title=f"전투중 - {monster_name}",
                color=discord.Color.green()
            )
            battle_ing_embed.add_field(name="내정보", value=f"💗 체력: {player_hp}")
            battle_ing_embed.add_field(name=f"{monster_name} 정보", value=f"💗 체력: {monster_hp}")
            battle_ing_embed.add_field(name="", value="", inline=True)

            battle_msg = await ctx.send(embed=battle_ing_embed)

            battle_ing_embed.add_field(name="전투 기록", value="", inline=False)

            while player_hp > 0 and monster_hp > 0:
                battle_ing_embed.add_field(name="", value="\n".join(battle_log), inline=False)

                # 메시지 수정
                await battle_msg.edit(embed=battle_ing_embed)

                await asyncio.sleep(1)

                damage = max(0, character_data['attack'] - monster_defense) 
                monster_hp -= damage
                battle_log.append(f"🗡 {character_data['name']}의 공격! {monster_name}한테 - {damage}의 피해 (남은 💗 HP:{monster_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if monster_hp <= 0:
                    dungeon_data['Experience'] += monster_exp
                    dungeon_data['Gold_Reward'] += monster_gold
                    await asyncio.sleep(2)
                    await dungeon_moster_clear(ctx, battle_msg, player_hp, monster_name)
                    return
                    
                await asyncio.sleep(1)

                damage = max(0, monster_attack - character_data['defense']) 
                player_hp -= damage
                battle_log.append(f"🗡 {monster_name}의 공격! {character_data['name']}한테 - {damage}의 피해 (남은 💗 HP:{player_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if player_hp <= 0:
                    await asyncio.sleep(2)
                    await dungeon_fail(ctx)
                    return
        else:
            battle_ing_embed = discord.Embed(  
                title=f"전투중 - {monster_name}",
                color=discord.Color.green()
            )
            battle_ing_embed.add_field(name="내정보", value=f"💗 체력: {player_hp}")
            battle_ing_embed.add_field(name=f"{monster_name} 정보", value=f"💗 체력: {monster_hp}")
            battle_ing_embed.add_field(name="", value="", inline=True)

            battle_msg = await ctx.send(embed=battle_ing_embed)

            battle_ing_embed.add_field(name="전투 기록", value="", inline=False)

            while player_hp > 0 and monster_hp > 0:
                battle_ing_embed.add_field(name="", value="\n".join(battle_log), inline=False)

                # 메시지 수정
                await battle_msg.edit(embed=battle_ing_embed)
                
                await asyncio.sleep(1)


                damage = max(0, monster_attack - character_data['defense']) 
                player_hp -= damage
                battle_log.append(f"🗡 {monster_name}의 공격! {character_data['name']}한테 - {damage}의 피해 (남은 💗 HP:{player_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if player_hp <= 0:
                    await asyncio.sleep(2)
                    await dungeon_fail(ctx)
                    return

                await asyncio.sleep(1)


                damage = max(0, character_data['attack'] - monster_defense) 
                monster_hp -= damage
                battle_log.append(f"🗡 {character_data['name']}의 공격! {monster_name}한테 - {damage}의 피해 (남은 💗 HP:{monster_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if monster_hp <= 0:
                    dungeon_data['Experience'] += monster_exp
                    dungeon_data['Gold_Reward'] += monster_gold
                    await asyncio.sleep(2)
                    await dungeon_moster_clear(ctx, battle_msg, player_hp, monster_name)
                    return

    elif dungeon_data['floor'] == 3:
        monster_types = {
            1: "마녀",
            2: "전령",
            3: "미믹",
            4: "드래곤"
        }

        monster_type = random.randint(1, 4)
        monster_name = monster_types[monster_type]

        # 몬스터 정보 가져오기
        monster_info = dungeon_monster_data[monster_name]
        monster_attack_speed = monster_info['🏹 공격속도']
        monster_info = dungeon_monster_data[monster_name]
        monster_hp = monster_info['체력']
        monster_attack = monster_info['공격력']
        monster_defense = monster_info['🛡 방어력']
        monster_exp = monster_info['경험치']
        monster_gold = monster_info['골드']

        if character_data['attack_speed'] >= monster_attack_speed:
            battle_ing_embed = discord.Embed(  
                title=f"전투중 - {monster_name}",
                color=discord.Color.green()
            )
            battle_ing_embed.add_field(name="내정보", value=f"💗 체력: {player_hp}")
            battle_ing_embed.add_field(name=f"{monster_name} 정보", value=f"💗 체력: {monster_hp}")
            battle_ing_embed.add_field(name="", value="", inline=True)

            battle_msg = await ctx.send(embed=battle_ing_embed)

            battle_ing_embed.add_field(name="전투 기록", value="", inline=False)

            while player_hp > 0 and monster_hp > 0:
                await battle_msg.edit(embed=battle_ing_embed)

                await asyncio.sleep(1)

                damage = max(0, character_data['attack'] - monster_defense) 
                monster_hp -= damage
                battle_log.append(f"🗡 {character_data['name']}의 공격! {monster_name}한테 - {damage}의 피해 (남은 💗 HP:{monster_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if monster_hp <= 0:
                    dungeon_data['Experience'] += monster_exp
                    dungeon_data['Gold_Reward'] += monster_gold
                    await asyncio.sleep(2)
                    await dungeon_moster_clear(ctx, battle_msg, player_hp, monster_name)
                    return
                    
                await asyncio.sleep(1)


                damage = max(0, monster_attack - character_data['defense']) 
                player_hp -= damage
                battle_log.append(f"🗡 {monster_name}의 공격! {character_data['name']}한테 - {damage}의 피해 (남은 💗 HP:{player_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if player_hp <= 0:
                    await asyncio.sleep(2)
                    await dungeon_fail(ctx)
                    return
        else:
            battle_ing_embed = discord.Embed(  
                title=f"전투중 - {monster_name}",
                color=discord.Color.green()
            )
            battle_ing_embed.add_field(name="내정보", value=f"💗 체력: {player_hp}")
            battle_ing_embed.add_field(name=f"{monster_name} 정보", value=f"💗 체력: {monster_hp}")
            battle_ing_embed.add_field(name="", value="", inline=True)

            battle_msg = await ctx.send(embed=battle_ing_embed)

            battle_ing_embed.add_field(name="전투 기록", value="", inline=False)

            while player_hp > 0 and monster_hp > 0:
                battle_ing_embed.add_field(name="", value="\n".join(battle_log), inline=False)

                # 메시지 수정
                await battle_msg.edit(embed=battle_ing_embed)
                
                await asyncio.sleep(1)


                damage = max(0, monster_attack - character_data['defense']) 
                player_hp -= damage
                battle_log.append(f"🗡 {monster_name}의 공격! {character_data['name']}한테 - {damage}의 피해 (남은 💗 HP:{player_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if player_hp <= 0:
                    await asyncio.sleep(2)
                    await dungeon_fail(ctx)
                    return

                await asyncio.sleep(1)


                damage = max(0, character_data['attack'] - monster_defense) 
                monster_hp -= damage
                battle_log.append(f"🗡 {character_data['name']}의 공격! {monster_name}한테 - {damage}의 피해 (남은 💗 HP:{monster_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if monster_hp <= 0:
                    dungeon_data['Experience'] += monster_exp
                    dungeon_data['Gold_Reward'] += monster_gold
                    await asyncio.sleep(2)
                    await dungeon_moster_clear(ctx, battle_msg, player_hp, monster_name)
                    return

    elif dungeon_data['floor'] == 4:
        monster_types = {
            1: "유령",
            2: "거인",
            3: "신수",
            4: "반신반인"
        }

        monster_type = random.randint(1, 4)
        monster_name = monster_types[monster_type]

        # 몬스터 정보 가져오기
        monster_info = dungeon_monster_data[monster_name]
        monster_attack_speed = monster_info['🏹 공격속도']
        monster_info = dungeon_monster_data[monster_name]
        monster_hp = monster_info['체력']
        monster_attack = monster_info['공격력']
        monster_defense = monster_info['🛡 방어력']
        monster_exp = monster_info['경험치']
        monster_gold = monster_info['골드']

        if character_data['attack_speed'] >= monster_attack_speed:
            battle_ing_embed = discord.Embed(  
                title=f"전투중 - {monster_name}",
                color=discord.Color.green()
            )
            battle_ing_embed.add_field(name="내정보", value=f"💗 체력: {player_hp}")
            battle_ing_embed.add_field(name=f"{monster_name} 정보", value=f"💗 체력: {monster_hp}")
            battle_ing_embed.add_field(name="", value="", inline=True)

            battle_msg = await ctx.send(embed=battle_ing_embed)

            battle_ing_embed.add_field(name="전투 기록", value="", inline=False)

            while player_hp > 0 and monster_hp > 0:
                battle_ing_embed.add_field(name="", value="\n".join(battle_log), inline=False)

                # 메시지 수정
                await battle_msg.edit(embed=battle_ing_embed)

                await asyncio.sleep(1)

                damage = max(0, character_data['attack'] - monster_defense) 
                monster_hp -= damage
                battle_log.append(f"🗡 {character_data['name']}의 공격! {monster_name}한테 - {damage}의 피해 (남은 💗 HP:{monster_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if monster_hp <= 0:
                    dungeon_data['Experience'] += monster_exp
                    dungeon_data['Gold_Reward'] += monster_gold
                    await asyncio.sleep(2)
                    await dungeon_moster_clear(ctx, battle_msg, player_hp, monster_name)
                    return
                    
                await asyncio.sleep(1)

                damage = max(0, monster_attack - character_data['defense']) 
                player_hp -= damage
                battle_log.append(f"🗡 {monster_name}의 공격! {character_data['name']}한테 - {damage}의 피해 (남은 💗 HP:{player_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if player_hp <= 0:
                    await asyncio.sleep(2)
                    await dungeon_fail(ctx)
                    return
        else:
            battle_ing_embed = discord.Embed(  
                title=f"전투중 - {monster_name}",
                color=discord.Color.green()
            )
            battle_ing_embed.add_field(name="내정보", value=f"💗 체력: {player_hp}")
            battle_ing_embed.add_field(name=f"{monster_name} 정보", value=f"💗 체력: {monster_hp}")
            battle_ing_embed.add_field(name="", value="", inline=True)

            battle_msg = await ctx.send(embed=battle_ing_embed)

            battle_ing_embed.add_field(name="전투 기록", value="", inline=False)

            while player_hp > 0 and monster_hp > 0:
                battle_ing_embed.add_field(name="", value="\n".join(battle_log), inline=False)

                # 메시지 수정
                await battle_msg.edit(embed=battle_ing_embed)
                
                await asyncio.sleep(1)

                damage = max(0, monster_attack - character_data['defense']) 
                player_hp -= damage
                battle_log.append(f"🗡 {monster_name}의 공격! {character_data['name']}한테 - {damage}의 피해 (남은 💗 HP:{player_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if player_hp <= 0:
                    await asyncio.sleep(2)
                    await dungeon_fail(ctx)
                    return

                await asyncio.sleep(1)

                damage = max(0, character_data['attack'] - monster_defense) 
                monster_hp -= damage
                battle_log.append(f"🗡 {character_data['name']}의 공격! {monster_name}한테 - {damage}의 피해 (남은 💗 HP:{monster_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if monster_hp <= 0:
                    dungeon_data['Experience'] += monster_exp
                    dungeon_data['Gold_Reward'] += monster_gold
                    await asyncio.sleep(2)
                    await dungeon_moster_clear(ctx, battle_msg, player_hp, monster_name)
                    return

    elif dungeon_data['floor'] == 5:
        monster_types = {
            1: "악마",
            2: "용사",
            3: "요정",
            4: "도깨비"
        }

        monster_type = random.randint(1, 4)
        monster_name = monster_types[monster_type]

        # 몬스터 정보 가져오기
        monster_info = dungeon_monster_data[monster_name]
        monster_attack_speed = monster_info['🏹 공격속도']
        monster_info = dungeon_monster_data[monster_name]
        monster_hp = monster_info['체력']
        monster_attack = monster_info['공격력']
        monster_defense = monster_info['🛡 방어력']
        monster_exp = monster_info['경험치']
        monster_gold = monster_info['골드']

        if character_data['attack_speed'] >= monster_attack_speed:
            battle_ing_embed = discord.Embed(  
                title=f"전투중 - {monster_name}",
                color=discord.Color.green()
            )
            battle_ing_embed.add_field(name="내정보", value=f"💗 체력: {player_hp}")
            battle_ing_embed.add_field(name=f"{monster_name} 정보", value=f"💗 체력: {monster_hp}")
            battle_ing_embed.add_field(name="", value="", inline=True)

            battle_msg = await ctx.send(embed=battle_ing_embed)

            battle_ing_embed.add_field(name="전투 기록", value="", inline=False)

            while player_hp > 0 and monster_hp > 0:
                battle_ing_embed.add_field(name="", value="\n".join(battle_log), inline=False)

                # 메시지 수정
                await battle_msg.edit(embed=battle_ing_embed)

                await asyncio.sleep(1)

                damage = max(0, character_data['attack'] - monster_defense) 
                monster_hp -= damage
                battle_log.append(f"🗡 {character_data['name']}의 공격! {monster_name}한테 - {damage}의 피해 (남은 💗 HP:{monster_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if monster_hp <= 0:
                    dungeon_data['Experience'] += monster_exp
                    dungeon_data['Gold_Reward'] += monster_gold
                    await asyncio.sleep(2)
                    await dungeon_moster_clear(ctx, battle_msg, player_hp, monster_name)
                    return
                    
                await asyncio.sleep(1)

                damage = max(0, monster_attack - character_data['defense']) 
                player_hp -= damage
                battle_log.append(f"🗡 {monster_name}의 공격! {character_data['name']}한테 - {damage}의 피해 (남은 💗 HP:{player_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if player_hp <= 0:
                    await asyncio.sleep(2)
                    await dungeon_fail(ctx)
                    return
        else:
            battle_ing_embed = discord.Embed(  
                title=f"전투중 - {monster_name}",
                color=discord.Color.green()
            )
            battle_ing_embed.add_field(name="내정보", value=f"💗 체력: {player_hp}")
            battle_ing_embed.add_field(name=f"{monster_name} 정보", value=f"💗 체력: {monster_hp}")
            battle_ing_embed.add_field(name="", value="", inline=True)

            battle_msg = await ctx.send(embed=battle_ing_embed)

            battle_ing_embed.add_field(name="전투 기록", value="", inline=False)

            while player_hp > 0 and monster_hp > 0:
                battle_ing_embed.add_field(name="", value="\n".join(battle_log), inline=False)

                # 메시지 수정
                await battle_msg.edit(embed=battle_ing_embed)
                
                await asyncio.sleep(1)

                damage = max(0, monster_attack - character_data['defense']) 
                player_hp -= damage
                battle_log.append(f"🗡 {monster_name}의 공격! {character_data['name']}한테 - {damage}의 피해 (남은 💗 HP:{player_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if player_hp <= 0:
                    await asyncio.sleep(2)
                    await dungeon_fail(ctx)
                    return

                await asyncio.sleep(1)

                damage = max(0, character_data['attack'] - monster_defense) 
                monster_hp -= damage
                battle_log.append(f"🗡 {character_data['name']}의 공격! {monster_name}한테 - {damage}의 피해 (남은 💗 HP:{monster_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if monster_hp <= 0:
                    dungeon_data['Experience'] += monster_exp
                    dungeon_data['Gold_Reward'] += monster_gold
                    await asyncio.sleep(2)
                    await dungeon_moster_clear(ctx, battle_msg, player_hp, monster_name)
                    return

    elif dungeon_data['floor'] == 6:
        monster_types = {
            1: "하피",
            2: "불의정령",
            3: "픽시",
            4: "거미여왕"
        }

        monster_type = random.randint(1, 4)
        monster_name = monster_types[monster_type]

        # 몬스터 정보 가져오기
        monster_info = dungeon_monster_data[monster_name]
        monster_attack_speed = monster_info['🏹 공격속도']
        monster_info = dungeon_monster_data[monster_name]
        monster_hp = monster_info['체력']
        monster_attack = monster_info['공격력']
        monster_defense = monster_info['🛡 방어력']
        monster_exp = monster_info['경험치']
        monster_gold = monster_info['골드']

        if character_data['attack_speed'] >= monster_attack_speed:
            battle_ing_embed = discord.Embed(  
                title=f"전투중 - {monster_name}",
                color=discord.Color.green()
            )
            battle_ing_embed.add_field(name="내정보", value=f"💗 체력: {player_hp}")
            battle_ing_embed.add_field(name=f"{monster_name} 정보", value=f"💗 체력: {monster_hp}")
            battle_ing_embed.add_field(name="", value="", inline=True)

            battle_msg = await ctx.send(embed=battle_ing_embed)

            battle_ing_embed.add_field(name="전투 기록", value="", inline=False)

            while player_hp > 0 and monster_hp > 0:
                battle_ing_embed.add_field(name="", value="\n".join(battle_log), inline=False)

                # 메시지 수정
                await battle_msg.edit(embed=battle_ing_embed)

                await asyncio.sleep(1)

                damage = max(0, character_data['attack'] - monster_defense) 
                monster_hp -= damage
                battle_log.append(f"🗡 {character_data['name']}의 공격! {monster_name}한테 - {damage}의 피해 (남은 💗 HP:{monster_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if monster_hp <= 0:
                    dungeon_data['Experience'] += monster_exp
                    dungeon_data['Gold_Reward'] += monster_gold
                    await asyncio.sleep(2)
                    await dungeon_moster_clear(ctx, battle_msg, player_hp, monster_name)
                    return
                    
                await asyncio.sleep(1)

                damage = max(0, monster_attack - character_data['defense']) 
                player_hp -= damage
                battle_log.append(f"🗡 {monster_name}의 공격! {character_data['name']}한테 - {damage}의 피해 (남은 💗 HP:{player_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if player_hp <= 0:
                    await asyncio.sleep(2)
                    await dungeon_fail(ctx)
                    return
        else:
            battle_ing_embed = discord.Embed(  
                title=f"전투중 - {monster_name}",
                color=discord.Color.green()
            )
            battle_ing_embed.add_field(name="내정보", value=f"💗 체력: {player_hp}")
            battle_ing_embed.add_field(name=f"{monster_name} 정보", value=f"💗 체력: {monster_hp}")
            battle_ing_embed.add_field(name="", value="", inline=True)

            battle_msg = await ctx.send(embed=battle_ing_embed)

            battle_ing_embed.add_field(name="전투 기록", value="", inline=False)

            while player_hp > 0 and monster_hp > 0:
                battle_ing_embed.add_field(name="", value="\n".join(battle_log), inline=False)

                # 메시지 수정
                await battle_msg.edit(embed=battle_ing_embed)
                
                await asyncio.sleep(1)

                damage = max(0, monster_attack - character_data['defense']) 
                player_hp -= damage
                battle_log.append(f"🗡 {monster_name}의 공격! {character_data['name']}한테 - {damage}의 피해 (남은 💗 HP:{player_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if player_hp <= 0:
                    await asyncio.sleep(2)
                    await dungeon_fail(ctx)
                    return

                await asyncio.sleep(1)

                damage = max(0, character_data['attack'] - monster_defense) 
                monster_hp -= damage
                battle_log.append(f"🗡 {character_data['name']}의 공격! {monster_name}한테 - {damage}의 피해 (남은 💗 HP:{monster_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if monster_hp <= 0:
                    dungeon_data['Experience'] += monster_exp
                    dungeon_data['Gold_Reward'] += monster_gold
                    await asyncio.sleep(2)
                    await dungeon_moster_clear(ctx, battle_msg, player_hp, monster_name)
                    return
                
    elif dungeon_data['floor'] == 7:
        monster_types = {
            1: "???",
        }

        monster_type = 1
        monster_name = monster_types[monster_type]

        # 몬스터 정보 가져오기
        monster_info = dungeon_monster_data[monster_name]
        monster_attack_speed = monster_info['🏹 공격속도'] + round(character_data['attack_speed'] / 50)
        monster_info = dungeon_monster_data[monster_name]
        monster_hp = monster_info['체력'] + round(character_data['hp'] / 10)
        monster_attack = monster_info['공격력'] + round(character_data['attack'] / 25)
        monster_defense = monster_info['🛡 방어력'] + round(character_data['defense'] /40)
        monster_exp = monster_info['경험치']
        monster_gold = monster_info['골드']

        if character_data['attack_speed'] >= monster_attack_speed:
            battle_ing_embed = discord.Embed(  
                title=f"전투중 - {monster_name}",
                color=discord.Color.green()
            )
            battle_ing_embed.add_field(name="내정보", value=f"💗 체력: {player_hp}")
            battle_ing_embed.add_field(name=f"{monster_name} 정보", value=f"💗 체력: {monster_hp}")
            battle_ing_embed.add_field(name="", value="", inline=True)

            battle_msg = await ctx.send(embed=battle_ing_embed)

            battle_ing_embed.add_field(name="전투 기록", value="", inline=False)

            while player_hp > 0 and monster_hp > 0:
                battle_ing_embed.add_field(name="", value="\n".join(battle_log), inline=False)

                # 메시지 수정
                await battle_msg.edit(embed=battle_ing_embed)

                await asyncio.sleep(1)

                damage = max(0, character_data['attack'] - monster_defense) 
                monster_hp -= damage
                battle_log.append(f"🗡 {character_data['name']}의 공격! {damage}의 피해 (남은 💗 HP:{monster_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if monster_hp <= 0:
                    dungeon_data['Experience'] += monster_exp
                    dungeon_data['Gold_Reward'] += monster_gold
                    await asyncio.sleep(2)
                    await dungeon_moster_clear(ctx, battle_msg, player_hp, monster_name)
                    return
                    
                await asyncio.sleep(1)

                damage = max(0, monster_attack - character_data['defense']) 
                player_hp -= damage
                battle_log.append(f"🗡 {monster_name}의 공격! {damage}의 피해 (남은 💗 HP:{player_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if player_hp <= 0:
                    await asyncio.sleep(2)
                    await dungeon_fail(ctx)
                    return
        else:
            battle_ing_embed = discord.Embed(  
                title=f"전투중 - {monster_name}",
                color=discord.Color.green()
            )
            battle_ing_embed.add_field(name="내정보", value=f"💗 체력: {player_hp}")
            battle_ing_embed.add_field(name=f"{monster_name} 정보", value=f"💗 체력: {monster_hp}")
            battle_ing_embed.add_field(name="", value="", inline=True)

            battle_msg = await ctx.send(embed=battle_ing_embed)

            battle_ing_embed.add_field(name="전투 기록", value="", inline=False)

            while player_hp > 0 and monster_hp > 0:
                battle_ing_embed.add_field(name="", value="\n".join(battle_log), inline=False)

                # 메시지 수정
                await battle_msg.edit(embed=battle_ing_embed)
                
                await asyncio.sleep(1)

                damage = max(0, monster_attack - character_data['defense']) 
                player_hp -= damage
                battle_log.append(f"🗡 {monster_name}의 공격! {character_data['name']}한테 - {damage}의 피해 (남은 💗 HP:{player_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if player_hp <= 0:
                    await asyncio.sleep(2)
                    await dungeon_fail(ctx)
                    return

                await asyncio.sleep(1)

                damage = max(0, character_data['attack'] - monster_defense) 
                monster_hp -= damage
                battle_log.append(f"🗡 {character_data['name']}의 공격! {monster_name}한테 - {damage}의 피해 (남은 💗 HP:{monster_hp})")

                await battle_msg.edit(embed=battle_ing_embed)

                if monster_hp <= 0:
                    dungeon_data['Experience'] += monster_exp
                    dungeon_data['Gold_Reward'] += monster_gold
                    await asyncio.sleep(2)
                    await dungeon_moster_clear(ctx, battle_msg, player_hp, monster_name)
                    return

async def dungeon_moster_clear(ctx, battle_msg, player_hp, monster_name):
    try:
        # 메시지가 존재하는 경우에만 삭제 시도
        await battle_msg.delete()
    except discord.errors.NotFound:
        # 메시지를 찾을 수 없을 경우 예외 처리
        pass


    dungeon_log.append(f"{monster_name}를 처리했습니다!")

    battle_end_embed = discord.Embed(  
        title=f"전투승리! - {monster_name}",
        color=discord.Color.blue()
    )
    battle_end_embed.add_field(name="내정보", value=f"💗 남은 체력: {player_hp}")
    
    result_msg = await ctx.send(embed=battle_end_embed)
    await asyncio.sleep(2)
    await result_msg.delete()

    # dungeon_data['floor']가 6보다 작거나 같으면 다음 층으로 이동
    if dungeon_data['floor'] <= 6:
        await dungeon_start(ctx, player_hp, dungeon_log)
    else:
        await clear_dungeon(ctx)


@bot.command(name="랭킹")
async def ranking(ctx):
    # Firebase에서 레벨 정보를 가져오기
    users_ref = db.collection('characters')
    docs = users_ref.stream()

    # 레벨 정보를 저장할 딕셔너리
    levels = {}

    for doc in docs:
        user_data = doc.to_dict()
        user_id = doc.id
        level = user_data.get('level', 0)
        levels[user_id] = level

    # 레벨을 기준으로 정렬
    sorted_levels = sorted(levels.items(), key=lambda x: x[1], reverse=True)

    # 랭킹을 표시할 Embed 생성
    ranking_embed = discord.Embed(title="레벨 랭킹", color=discord.Color.gold())

    # 상위 10명의 랭킹을 Embed에 추가
    for i, (user_id, level) in enumerate(sorted_levels[:10]):
        member = await bot.fetch_user(int(user_id))
        if member:
            if i == 0:
                ranking_embed.add_field(name=f"🥇 1등", value=f"{member.name} - 레벨 {level}", inline=False)
            elif i == 1:
                ranking_embed.add_field(name=f"🥈 2등", value=f"{member.name} - 레벨 {level}", inline=False)
            elif i == 2:
                ranking_embed.add_field(name=f"🥉 3등", value=f"{member.name} - 레벨 {level}", inline=False)
            else:
                ranking_embed.add_field(name=f"{i+1}등", value=f"{member.name} - 레벨 {level}", inline=False)

    await ctx.send(embed=ranking_embed)

@bot.command(name='정보')
async def show_info(ctx):
    # 캐릭터 정보 조회 및 Embed로 꾸며서 출력
    user_id = str(ctx.author.id)
    doc_ref = db.collection('characters').document(user_id)
    doc = doc_ref.get()

    if doc.exists:
        character_data = doc.to_dict()

        if 'inventory' not in character_data:
            # 인벤토리 정보가 없으면 새로 생성
            character_data['inventory'] = {
                '루비': 0,
                '구리': 0,
                '금': 0,
                '에메랄드': 0,
                '다이아몬드': 0,
                '자수정': 0,
                '나무': 0,
                '흑요석': 0,
                '철': 0,
            }
            doc_ref.set(character_data)

        if 'equipment' not in character_data:
            # 장비 정보가 없으면 새로 생성
            character_data['equipment'] = []
            doc_ref.set(character_data)

        current_level = character_data['level']
        exp_required = calculate_exp_required(current_level)

        # Embed 생성
        embed = discord.Embed(
            title=f"{character_data['name']}의 캐릭터 정보",
            color=discord.Color.blue()
        )
        embed.add_field(name="🌟 레벨: ", value=character_data["level"], inline=False)
        embed.add_field(name="💗 HP: ", value=character_data["hp"])
        embed.add_field(name="🗡 공격력: ", value=character_data["attack"])
        embed.add_field(name="🛡 방어력: ", value=character_data["defense"])
        embed.add_field(name="✨ 경험치: ", value=f"{exp_required} / {character_data['exp']}")
        embed.add_field(name="🏹 공격속도: ", value=character_data["attack_speed"])
        embed.add_field(name="💰 돈: ", value=character_data["gold"])
        
        # 장비 정보 추가
        equipment_info = "\n".join([f"{item}: {', '.join([f'{stat} {value}' for stat, value in stats.items()])}" for item, stats in character_data.get("장비", {}).items()])
        embed.add_field(name="🎽 보물: ", value=equipment_info or "보물 없음")

        await ctx.send(embed=embed)
    else:
        await ctx.send('아직 캐릭터를 생성하지 않았습니다. `희루야 캐릭터생성 [이름]`으로 캐릭터를 생성해주세요.')

@bot.command(name='인벤토리', aliases=['인벤', '가방'])
async def show_inventory(ctx):
    user_id = str(ctx.author.id)
    doc_ref = db.collection('characters').document(user_id)
    character_data = doc_ref.get().to_dict()

    if 'inventory' not in character_data:
        # 인벤토리 정보가 없으면 새로 생성
        character_data['inventory'] = {
            '루비': 0,
            '구리': 0,
            '금': 0,
            '에메랄드': 0,
            '다이아몬드': 0,
            '자수정': 0,
            '나무': 0,
            '흑요석': 0,
            '철': 0,
        }
        doc_ref.set(character_data)

    inventory_data = character_data['inventory']

    # Embed 생성
    inventory_embed = discord.Embed(
        title=f"{character_data['name']}의 가방",
        color=discord.Color.green()
    )
    inventory_embed.description = "가방을 한번 볼까요~?"

    # 인벤토리 데이터 반복해서 Embed에 추가
    for item_name, quantity in inventory_data.items():
        emoji = get_item_emoji(item_name)
        inventory_embed.add_field(name=f"{emoji} {item_name}", value=f"{quantity}개", inline=True)

    await ctx.send(embed=inventory_embed)

def get_item_emoji(item_name):
    emojis = {
        '루비': '🟥',
        '구리': '🟧',
        '금': '🟨',
        '에메랄드': '🟩',
        '다이아몬드': '🟦',
        '자수정': '🟪',
        '나무': '🟫',
        '흑요석': '⬛',
        '철': '⬜',
    }
    return emojis.get(item_name, '❓')

def get_category_emoji(category_name):
    category_name = category_name.lower()
    if category_name == '무기':
        return '⚔️'
    elif category_name == '보조무기':
        return '🏹'
    elif category_name == '갑옷':
        return '🛡️'
    elif category_name == '목걸이':
        return '📿'
    else:
        return '❓'


@bot.command(name='제작법')
async def show_crafting_options(ctx, category=None):
    user_id = str(ctx.author.id)
    doc_ref = db.collection('characters').document(user_id)
    character_data = doc_ref.get().to_dict()

    crafting_recipes = {
        '무기': {
            '철검': {'⬜ 철': 200, '🟫 나무': 50},
            '금검': {'🟨 금': 200, '⬜ 철': 100, '🟫 나무': 50},
            '다이아검': {'🟦 다이아몬드': 200, '⬜ 철': 100, '🟫 나무': 50},
        },
        '보조무기': {
            '활': {'🟫 나무': 150, '⬜ 철': 50},
            '마법봉': {'🟫 나무': 100, '🟪 자수정': 50},
            '투척용품': {'⬜ 철': 100, '🟨 금': 50, '🟫 나무': 30},
        },
        '갑옷': {
            '가죽갑옷': {'🟫 나무': 200},
            '금갑옷': {'🟨 금': 300},
            '다이아몬드갑옷': {'🟦 다이아몬드': 400, '🟨 금': 200},
        },
        '목걸이': {
            '힘의목걸이': {'⬜ 철': 150, '🟪 자수정': 100, '🟩 에메랄드': 100},
            '방어의목걸이': {'🟨 금': 200, '🟦 다이아몬드': 150, '🟧 구리': 100},
            '민첩의목걸이': {'🟨 금': 100, '🟪 자수정': 50, '🟫 나무': 30},
        },
    }
    if not category:
        # 카테고리가 주어지지 않은 경우, 모든 카테고리 보여주기
        options_embed = discord.Embed(
            title=f"{character_data['name']}의 제작 가능한 종류",
            color=discord.Color.blue()
        )
        options_embed.description = "무슨 아이템을 제작하고 싶으세요?"

        for category_name in crafting_recipes.keys():
            options_embed.add_field(name=category_name, value=f"`희루야 제작법 {category_name}`", inline=True)

        await ctx.send(embed=options_embed)

    elif category.lower() in crafting_recipes:
        # 특정 카테고리의 제작법 보여주기
        category_lower = category.lower()
        recipes_embed = discord.Embed(
            title=f"{character_data['name']}의 {category} 제작법",
            color=discord.Color.blue()
        )
        category_recipes = crafting_recipes[category_lower]

        for item_name, ingredients in category_recipes.items():
            emoji = get_item_emoji(item_name)
            recipe_text = ', '.join([f"{ingredient} {amount}" for ingredient, amount in ingredients.items()])
            recipes_embed.add_field(name=f"{item_name} 제작법", value=recipe_text, inline=False)

        await ctx.send(embed=recipes_embed)
    else:
        await ctx.send(f"해당 카테고리의 제작법이 없습니다. 유효한 카테고리를 입력하세요.")

@bot.command(name='재료상점', aliases=['재료 상점'])
async def show_material_shop(ctx):
    shop_items = {
        '루비': 1000,
        '구리': 500,
        '금': 700,
        '에메랄드': 4000,
        '다이아몬드': 5000,
        '자수정': 7500,
        '나무': 200,
        '흑요석': 2500,
        '철': 250,
    }

    shop_embed = discord.Embed(
        title="희루의 재료 상점",
        color=discord.Color.gold()
    )
    shop_embed.description = "무엇을 구매하시겠어요❓ (개당)\n구매 방법💸: '희루야 재료구매 [재료] [개수]'\n"
    shop_embed.add_field(name="", value="",inline=False)

    for item, price in shop_items.items():
        emoji = get_item_emoji(item)
        shop_embed.add_field(name=f"{emoji} {item}", value=f"가격: {price}원", inline=True)

    await ctx.send(embed=shop_embed)

@bot.command(name='재료구매')
async def buy_material(ctx, item_name, quantity: int):
    user_id = str(ctx.author.id)
    doc_ref = db.collection('characters').document(user_id)
    character_data = doc_ref.get().to_dict()

    # 상점에서 판매하는 아이템 및 가격 설정
    shop_items = {
        '루비': 1000,
        '구리': 500,
        '금': 700,
        '에메랄드': 4000,
        '다이아몬드': 5000,
        '자수정': 7500,
        '나무': 200,
        '흑요석': 2500,
        '철': 250,
    }

    # 입력받은 아이템이 상점에 있는지 확인
    if item_name in shop_items:
        # 필요한 골드 계산
        total_price = shop_items[item_name] * quantity

        # 보유한 골드 확인
        if 'gold' not in character_data:
            character_data['gold'] = 0

        if character_data['gold'] >= total_price:
            # 골드 차감 및 아이템 수량 증가
            character_data['gold'] -= total_price

            # 인벤토리에 아이템 추가 또는 수량 증가
            if item_name not in character_data['inventory']:
                character_data['inventory'][item_name] = quantity
            else:
                character_data['inventory'][item_name] += quantity

            # 업데이트된 캐릭터 데이터를 저장
            doc_ref.update(character_data)

            await ctx.send(f"{item_name}을(를) {quantity}개({total_price}) 구매하셨습니다!")
        else:
            await ctx.send("골드가 부족해요. 구매할 수 없습니다.")
    else:
        await ctx.send("그런 재료는 판매하지 않아요. 확인해주세요.")








































































bot.run(os.environ['MTExMTU2NjAyNjc1NzM5NDQ3Mw.Ghbokp.PBmdNIKSGUem_IcL_rswdMDCY32nGm7sRZ1SqE'])
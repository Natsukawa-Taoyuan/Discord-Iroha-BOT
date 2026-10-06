import discord
from discord.ext import commands, tasks
from discord import app_commands
import sys
import io
import json
import os
import random
import datetime
import asyncio
import aiohttp
import urllib.request
import math

TOKEN = 'YOUR_DISCORD_BOT_TOKEN_HERE'
CONSOLE_CHANNEL_ID = 'YOUR_CONSOLE_CHANNEL_ID_HERE'
DEV_ID = [YOUR_DISCORD_USER_ID_HERE]  
DATA_FILE = 'iroha_data.json'

TAG_IMAGE_URL = "https://cdn.discordapp.com/attachments/1462516952936484935/1462524920516051024/491071f7-40af-42fd-844d-e8a95ce23522-profile_banner-480.png"
PATRICK_GIF = "https://cdn.discordapp.com/attachments/1462516952936484935/1462517044699201789/patrick_star_eating_GIF_by_SpongeBob_SquarePants.gif"
BONK_IMAGES = [
    "https://cdn.discordapp.com/attachments/1462516952936484935/1462548772302098564/bonk-doge_1.gif",
    "https://cdn.discordapp.com/attachments/1462516952936484935/1462548800534216765/bonk-doge.gif"
]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='i!', intents=intents, help_command=None)

log_buffer = ""
class IrohaLogger(io.TextIOBase):
    def write(self, s):
        global log_buffer
        sys.__stdout__.write(s)
        log_buffer += str(s)
        if len(log_buffer) > 4000: log_buffer = log_buffer[-4000:]
        return len(s)
    def flush(self): sys.__stdout__.flush()

sys.stdout = IrohaLogger()
sys.stderr = IrohaLogger()

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"users": {}, "guilds": {}}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_guild_config(guild_id):
    data = load_data()
    gid = str(guild_id)
    return data["guilds"].get(gid, {})

def update_guild_config(guild_id, key, value):
    data = load_data()
    gid = str(guild_id)
    if gid not in data["guilds"]:
        data["guilds"][gid] = {}
    data["guilds"][gid][key] = value
    save_data(data)

def cat_talk(text):
    """將文字轉換為貓娘語氣"""
    return f"🐾 **{text} 喵～**"

def is_master():
    """判斷是否為指揮官 (開發者)"""
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id in DEV_ID
    return app_commands.check(predicate)

@tasks.loop(seconds=5)
async def report_log():
    await bot.wait_until_ready()
    global log_buffer
    if not log_buffer.strip(): return
    
    try:
        channel = bot.get_channel(int(CONSOLE_CHANNEL_ID)) or await bot.fetch_channel(int(CONSOLE_CHANNEL_ID))
        if channel:
            content = log_buffer[-1900:]
            await channel.send(f"🌸 **[彩葉的勤務紀錄]**\n```text\n{content}\n```")
            log_buffer = ""
    except Exception:
        pass

class IrohaEntertainment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mission_lock = asyncio.Lock() 
        if not self.krabby_patty_alarm.is_running():
            self.krabby_patty_alarm.start()

    @app_commands.command(name="iroha_remote_on", description="[開發者專屬] 遠端幫特定伺服器開啟蟹堡功能")
    @app_commands.describe(guild_id="目標伺服器 ID", channel_id="發送蟹堡的頻道 ID")
    async def iroha_remote_on(self, interaction: discord.Interaction, guild_id: str, channel_id: str):
        await interaction.response.defer(ephemeral=True)

        if interaction.user.id not in DEV_ID:
            return await interaction.followup.send("❌ 權限不足", ephemeral=True)

        clean_guild_id = "".join(filter(str.isdigit, guild_id))
        clean_channel_id = "".join(filter(str.isdigit, channel_id))

        if not clean_guild_id or not clean_channel_id:
            return await interaction.followup.send("❌ ID 格式錯誤", ephemeral=True)

        update_guild_config(clean_guild_id, "channel_3am", int(clean_channel_id))
        update_guild_config(clean_guild_id, "enable_3am", True)
        update_guild_config(clean_guild_id, "dev_forced", True)
        
        await interaction.followup.send(cat_talk(f"✅ 伺服器 `{clean_guild_id}` 已完成無痕對接！頻道：<#{clean_channel_id}>"), ephemeral=True)

    @tasks.loop(time=datetime.time(hour=3, minute=0, tzinfo=datetime.timezone(datetime.timedelta(hours=8))))
    async def krabby_patty_alarm(self):
        await self.bot.wait_until_ready()
        
        tw_tz = datetime.timezone(datetime.timedelta(hours=8))
        today_str = datetime.datetime.now(tw_tz).strftime("%Y-%m-%d")

        async with self.mission_lock:
            for guild in self.bot.guilds:
                config = get_guild_config(guild.id)
                
                if not config.get("enable_3am", False): 
                    continue

                target_channel_id = config.get("channel_3am")
                if not target_channel_id:
                    continue
                
                if config.get("last_burger_sent_date") == today_str:
                    continue
                    
                target_channel = self.bot.get_channel(int(target_channel_id))
                if target_channel:
                    try:
                        update_guild_config(guild.id, "last_burger_sent_date", today_str)
                        
                        embed = discord.Embed(
                            title="🍔 好棒喔！凌晨三點了！",
                            description="**是時候吃美味蟹堡了！**",
                            color=0xff9900
                        )
                        embed.set_image(url=PATRICK_GIF)
                        await target_channel.send(embed=embed)
                        print(f"🍔 [無痕任務] 已成功幫伺服器 {guild.name} 送達蟹堡")
                    except Exception as e:
                        print(f"❌ 無痕任務失敗 ({guild.name}): {e}")
                                            
    @app_commands.command(name="iroha_setup", description="[管理員] 開關彩葉的各項服務模組")
    @app_commands.describe(feature="要設定的功能", state="開啟或關閉")
    @app_commands.choices(feature=[
        app_commands.Choice(name="日常問候(早午晚)", value="greetings"), 
        app_commands.Choice(name="凌晨三點蟹堡", value="3am"),
        app_commands.Choice(name="被Tag時保護主人", value="tag"),
        app_commands.Choice(name="不可以色色(敲頭)", value="bonk"),
        app_commands.Choice(name="機率運算(Roll)", value="roll"),
        app_commands.Choice(name="運勢預測(Luck)", value="luck"),
        app_commands.Choice(name="機密彩蛋", value="egg")
    ], state=[
        app_commands.Choice(name="開啟", value="on"),
        app_commands.Choice(name="關閉", value="off")
    ])
    @app_commands.default_permissions(administrator=True)
    async def iroha_setup(self, interaction: discord.Interaction, feature: str, state: str):
        is_on = (state == "on")
        config_key = f"enable_{feature}"
        update_guild_config(interaction.guild_id, config_key, is_on)
        
        status_text = "開啟" if is_on else "關閉"
        await interaction.response.send_message(cat_talk(f"已經幫主人把 `{feature}` 模組 **{status_text}** 了喵！"), ephemeral=True)

    @app_commands.command(name="iroha_set_channel", description="[管理員] 指定彩葉送美味蟹堡的頻道")
    @app_commands.default_permissions(administrator=True)
    async def iroha_set_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        update_guild_config(interaction.guild_id, "channel_3am", channel.id)
        update_guild_config(interaction.guild_id, "enable_3am", True)
        await interaction.response.send_message(cat_talk(f"記住了喵！彩葉會在凌晨 3:00 把美味蟹堡送到 {channel.mention} 喔！"))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return

        config = get_guild_config(message.guild.id)
        if config.get("enable_tag", False):
            mentioned_ids = [user.id for user in message.mentions]      
            if any(uid in DEV_ID for uid in mentioned_ids):
                try:
                    embed = discord.Embed(
                        title="👀 找主人有事嗎喵？", 
                        description="主人現在可能在忙，請不要隨便打擾他喵！",
                        color=0xff0000
                    )
                    embed.set_image(url=TAG_IMAGE_URL)
                    await message.reply(embed=embed)
                except Exception as e:
                    print(f"❌ Tag 回覆失敗: {e}")

    @app_commands.command(name="bonk", description="[全員] 匿名敲壞壞的人的頭")
    async def bonk(self, interaction: discord.Interaction, member: discord.Member):
        config = get_guild_config(interaction.guild_id)
        if not config.get("enable_bonk", False):
            return await interaction.response.send_message(cat_talk("主人，這個功能還沒有開啟喵～"), ephemeral=True)

        chosen_image = random.choice(BONK_IMAGES)
        embed = discord.Embed(
            title="🐕 不可以色色喵！(Bonk!)",
            description=f"{member.mention} **\n您的言論已經涉及到色情成人內容🫵😡 \n彩葉要制裁你了喵！⚖️ \n請速速移至成人頻道，不然彩葉會生氣的喵！🔞**",
            color=0xff0000
        )
        embed.set_image(url=chosen_image)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="vtuber", description="(Hidden) 彩葉偷偷推薦的 VTubers")
    async def vtuber(self, interaction: discord.Interaction):
        config = get_guild_config(interaction.guild_id)        
        if not config.get("enable_egg", False):
            return await interaction.response.send_message(cat_talk("這個頻道還沒解鎖喵..."), ephemeral=True)
    
        variations = [
            {
                "text": "**來自主人的推薦喵:**\n快去推她喵！她超級可愛的！\n[YouTube](https://www.youtube.com/@chiharu_piao1115) [Instagram](https://www.instagram.com/chiharu_piao/)",
                "image": "https://cdn.discordapp.com/attachments/1462516952936484935/1463255708861730925/480966268_1213229833814300_723541416855806782_n_upscayl_4x_high-fidelity-4x.png?ex=69712a92&is=696fd912&hm=965378a6d0cac9dba3b3c4e107e2774bc865e4998d0ffaab20f15a058cdb0451",
                "color": 0xCA8EFF
            },
            {
                "text": "**來自主人的推薦喵:**\n這可是主人的最愛！快去追蹤她喵！\n[YouTube](https://www.youtube.com/@NatsuiroMatsuri) [Twitter](https://x.com/natsuiromatsuri)",
                "image": "https://cdn.discordapp.com/attachments/1462516952936484935/1463287173045551294/GALE8D-bkAAdBs9_upscayl_6x_high-fidelity-4x.png?ex=697147e0&is=696ff660&hm=e55d11faa728f52065ac0e1c8b19082c7c8149ef48d57afb1d1355cdc07483ea",
                "color": 0xFF8000
            },
            {
                "text": "**來自主人的推薦喵:**\n超級可愛的台V！主人很喜歡她喔！\n[YouTube](https://www.youtube.com/@udngame) [Twitter](https://x.com/udngameyunai)",
                "image": "https://cdn.discordapp.com/attachments/1462516952936484935/1463288580259713280/G1FmgxkaQAE4kUQ_upscayl_4x_high-fidelity-4x.png?ex=69714930&is=696ff7b0&hm=96a7f013dc919f989e32552eb2e45e7ab3b0f87739d18066ec72b07cd3e2cc71",
                "color": 0xFF8000
            }
        ]

        chosen = random.choice(variations)
        embed = discord.Embed(
            title="🔒 彩葉的機密推播",
            description=chosen["text"],
            color=chosen["color"]
        )
        embed.set_image(url=chosen['image'])
        embed.set_footer(text=f"觸發者: {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roll", description="[全員] 啟動彩葉的隨機數生成器")
    async def roll(self, interaction: discord.Interaction, max_num: int = 100):
        config = get_guild_config(interaction.guild_id)
        if not config.get("enable_roll", False):
            return await interaction.response.send_message(cat_talk("主人，這個功能還沒有開啟喵～"), ephemeral=True)
        
        if max_num <= 1:
            return await interaction.response.send_message(cat_talk("嗚喵？骰子至少要有兩面彩葉才能丟呀！"), ephemeral=True)

        result = random.randint(1, max_num)
        percent = (result / max_num) * 100
        
        if result == max_num:
            comment = "🌟 **太神奇了！機率 100%！彩葉幫你按摩慶祝喵！** 🐾"
            color = 0xf1c40f 
        elif result == 1:
            comment = "💀 **嗚哇... 只有 1... 彩葉會給您抱抱安慰的喵！**"
            color = 0x000000 
        elif percent >= 80:
            comment = "🔥 **數值很高喵！看來今天運氣真好！**"
            color = 0xe74c3c 
        elif percent <= 20:
            comment = "🌧️ **數值有點低... 需要彩葉幫你吹一吹骰子嗎喵？**"
            color = 0x607d8b 
        elif percent == 69:
            comment = "😏 **喵嘿嘿，Nice 喵。**"
            color = 0xe91e63 
        else:
            comment = "🤖 **計算完畢！這就是命運喵！**"

        embed = discord.Embed(
            title="🎲 彩葉幫你丟骰子喵",
            description=f"{interaction.user.mention} 啟動了隨機數生成器 (1-{max_num})...",
            color=color
        )
        embed.add_field(name="運算數據", value=f"## 🎲 {result}", inline=False)
        embed.add_field(name="彩葉的分析", value=comment, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="luck", description="[全員] 讓彩葉幫你測測今天的運勢")
    async def luck(self, interaction: discord.Interaction):
        config = get_guild_config(interaction.guild_id)
        if not config.get("enable_luck", False):
            return await interaction.response.send_message(cat_talk("運勢分析還沒準備好喵，請稍後再試！"), ephemeral=True)

        fortunes = [
            {"type": "✨ 大吉 (Legendary)", "color": 0xf1c40f, "desc": "哇喵！彩葉查過了，您今天是SSR級的運氣喵！抽卡一定中！"},
            {"type": "🔥 中吉 (Epic)",      "color": 0x9b59b6, "desc": "運氣很好喵！今天玩遊戲一定能贏，彩葉會在旁邊幫您加油的！"},
            {"type": "🔹 小吉 (Rare)",      "color": 0x3498db, "desc": "普普通通的幸運喵～彩葉會為您祈禱，讓好事發生的！"},
            {"type": "☁️ 末吉 (Common)",     "color": 0x95a5a6, "desc": "運氣平平喵... 出門要小心喔，彩葉會等您回來的。"},
            {"type": "💀 大凶 (Error)",      "color": 0x000000, "desc": "嗚嗚，感測到厄運喵... 您今天還是乖乖待在彩葉身邊吧！"}
        ]
        tips = [
            "多摸摸彩葉的頭", "喝杯熱牛奶", "今天適合玩輔助", 
            "跟彩葉一起玩遊戲", "先睡個午覺喵", "不要相信直覺，相信彩葉"
        ]

        result = random.choice(fortunes)
        lucky_percent = random.randint(1, 100)
        random_tip = random.choice(tips)

        embed = discord.Embed(
            title=f"🔮 {interaction.user.display_name} 的今日運勢喵",
            description="正在連線至貓娘資料庫... 分析完畢！🐾",
            color=result["color"]
        )
        embed.add_field(name="運勢等級", value=f"### {result['type']}", inline=False)
        embed.add_field(name="幸運指數", value=f"**{lucky_percent}%**", inline=True)
        embed.add_field(name="彩葉的建議", value=f"「{random_tip}」", inline=True)
        embed.add_field(name="詳細分析", value=result["desc"], inline=False)
        
        if interaction.user.display_avatar:
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text="僅供參考喵！如果運氣不好，可以多來找彩葉玩喔！")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="[全員] 查看彩葉的所有服務與指令喵")
    async def help(self, interaction: discord.Interaction):
        is_admin = interaction.user.guild_permissions.administrator
        is_master = interaction.user.id in DEV_ID

        greeting = "主人歡迎回來喵！" if is_master else "歡迎您！"

        embed = discord.Embed(
            title="🐾 彩葉的服務菜單喵",
            description=f"{greeting} 以下是彩葉目前可以為您提供的服務喔！",
            color=0xCA8EFF
        )
        
        fun_desc = (
            "💬 **日常問候** - 在頻道說早安/午安/晚安，彩葉會回應您喔喵！\n"
            "🎲 `/roll [數字]` - 讓彩葉幫您丟骰子\n"
            "🔮 `/luck` - 讓彩葉幫您測算今日運勢\n"
            "🔨 `/bonk [@某人]` - 制裁發言色色的人喵！\n"
            "ℹ️ `/about` - 關於彩葉的身世與服務說明"
        )
        embed.add_field(name="🎮 常規娛樂與互動服務", value=fun_desc, inline=False)

        if is_admin or is_master:
            admin_desc = (
                "🎛️ `/iroha_setup` - 開關彩葉的各項功能模組 (包含問候、抽獎等)\n"
                "🍔 `/iroha_set_channel` - 指定凌晨三點美味蟹堡的發送頻道"
            )
            embed.add_field(name="⚙️ 管理員設定中心", value=admin_desc, inline=False)

        if is_master:
            secret_desc = (
                "📁 `/secret` - 查閱主人的機密檔案\n"
                "📺 `/vtuber` - 查看彩葉的私藏推薦\n"
                "💻 `i!dev` - (文字指令) 召喚隱藏的開發者控制台"
            )
            embed.add_field(name="🤫 主人專屬機密", value=secret_desc, inline=False)

        if self.bot.user.display_avatar:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            
        embed.set_footer(text="如果有其他吩咐，隨時呼叫彩葉喵！🐾")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="about", description="[全員] 查看彩葉的身世與服務條款喵")
    async def about(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="ℹ️ 關於彩葉 (Iroha) 喵🐾", 
            description="您的 Discord 伺服器專屬貓娘女僕小幫手", 
            color=0xCA8EFF 
        )
        embed.add_field(name="👨‍💻 開發者 (主人)", value="桃源三橘義 (natsukawa0707)", inline=False)
        
        tos = (
            "本機器人為非商業 Side Project，免費提供給有需要的群組使用，旨在提供自動化管理並減輕管理員的負擔喵！\n\n"
            "🖥️ **部署環境**\n"
            "部署於 Proxmox VE 私有雲環境，提供 24 小時不間斷的自動化服務。\n\n"
            "⚠️ **免責聲明**\n"
            "機器人由開發者單人維護及檢修，**不保證** 100% 穩定或長期提供服務。\n"
            "開發者保有修改功能、退出違規伺服器、發布公告或廣告之權利，恕不另行通知。\n\n"
            "🤝 **功能請求**\n"
            "若群主有功能需求，歡迎直接私訊說明，但開發者保有拒絕或排程之權利。\n\n"
            "✅ **同意條款**\n"
            "使用本機器人即表示同意以上條款，並理解開發者無法提供義務性支援。\n"
            "如有任何建議，歡迎聯絡主人，謝謝您的理解及支持喵！\n\n"
            "🌐 **開發者網頁**\n"
            "https://natsukawataoyuan.com/\n\n"
            "📊 **伺服器狀態**\n"
            "https://status.natsukawataoyuan.com/status/mystatus"
        )
        embed.add_field(name="📜 服務說明與條款", value=tos, inline=False)
        
        if interaction.user.display_avatar:
            embed.set_footer(text=f"查詢者: {interaction.user.display_name} | 彩葉為您服務喵🐾", icon_url=interaction.user.display_avatar.url)
        else:
            embed.set_footer(text=f"查詢者: {interaction.user.display_name} | 彩葉為您服務喵🐾")
            
        await interaction.response.send_message(embed=embed)

class DevPanelView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None) 
        self.bot = bot

    @discord.ui.button(label="同步斜線指令", style=discord.ButtonStyle.green, emoji="🔄")
    async def btn_sync(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in DEV_ID: return
        await interaction.response.send_message(cat_talk("彩葉正在幫主人同步指令喵..."), ephemeral=True)
        try:
            synced = await self.bot.tree.sync()
            await interaction.edit_original_response(content=cat_talk(f"同步完成喵！目前共有 {len(synced)} 個斜線指令準備就緒！"))
        except Exception as e:
            await interaction.edit_original_response(content=cat_talk(f"嗚嗚，同步失敗了：{e}"))

    @discord.ui.button(label="系統狀態", style=discord.ButtonStyle.blurple, emoji="📊")
    async def btn_status(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in DEV_ID: return
        latency = round(self.bot.latency * 1000)
        guild_count = len(self.bot.guilds)
        user_count = sum(g.member_count for g in self.bot.guilds)
        
        embed = discord.Embed(title="📊 彩葉的健康檢查報告", color=0x3498db)
        embed.add_field(name="🏓 延遲 (Ping)", value=f"{latency} ms", inline=True)
        embed.add_field(name="🏢 服務伺服器", value=f"{guild_count} 個", inline=True)
        embed.add_field(name="👥 服務總人數", value=f"{user_count} 人", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="機密檔案庫", style=discord.ButtonStyle.gray, emoji="🔐")
    async def btn_archive(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in DEV_ID: return
        
        secret_content = (
            "主人辛苦了喵！這是我私下為您整理的「彩蛋解答」與「開發紀錄」：\n\n"
            "✨ **彩蛋解答：**\n"
            "原本馬文身上的 `marvin` 指令其實隱藏了主人的推廣網址喵！\n"
            "而現在 `/secret` 裡面那張照片，其實是主人珍藏的 Cosplay 紀念照呢喵～\n\n"
            "🛠️ **系統真實狀態：**\n"
            f"• 彩葉的專屬帳本 `{DATA_FILE}` 運作良好喵！\n"
            f"• 目前已記錄了 {len(load_data()['users'])} 位主人的朋友們喵。\n"
            "• 伺服器同步線路：穩定連線至主人的 Proxmox VE 私有雲喵！\n\n"
            "💖 **彩葉的悄悄話：**\n"
            "謝謝主人把我從馬文身上拆分出來，讓我能擁有自己的名字「彩葉」。\n"
            "我會一直守護主人的娛樂頻道，絕對不會讓壞人踩進主人的秘密基地喵！"
        )
        embed = discord.Embed(
            title="🐾 彩葉的私密收件匣",
            description=secret_content,
            color=0x2f3136 
        )
        if self.bot.user.display_avatar:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="⚠️ 本訊息僅限主人查看，對話框關閉後即消失喵。")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="強制休眠", style=discord.ButtonStyle.red, emoji="🛑")
    async def btn_shutdown(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in DEV_ID: return
        await interaction.response.send_message(cat_talk("主人晚安... 彩葉要進入休眠模式了喵... 💤"), ephemeral=True)
        await self.bot.close()

@bot.command(name="dev", hidden=True)
@commands.check(lambda ctx: ctx.author.id in DEV_ID)
async def dev_panel(ctx):
    """(隱藏指令) 召喚開發者面板"""
    embed = discord.Embed(
        title="⚙️ 彩葉的終端控制台",
        description="主人辛苦了！請選擇您要執行的系統操作喵：",
        color=0x2c3e50
    )
    embed.set_footer(text="⚠️ 這些按鈕只有主人按了才會有反應喵！")
    await ctx.send(embed=embed, view=DevPanelView(bot))

@dev_panel.error
async def dev_panel_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        pass 

class IrohaGreetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        config = get_guild_config(message.guild.id)
        if not config.get("enable_greetings", True):
            return

        content = message.content.lower()
        user_name = message.author.display_name
        is_director = (message.author.id in DEV_ID) 

        if any(keyword in content for keyword in ["早安", "早啊", "早上好", "good morning", "早!"]):
            if is_director:
                replies = [
                    f"早安，最偉大的 {user_name} 總監大人！彩葉已經幫您泡好特製的貓草咖啡了喵！(蹭蹭)☕🐾",
                    f"嗚喵～是 {user_name} 主人！今天伺服器的程式碼也都乖乖的喔！總監早安喵！✨",
                    f"總監早安！彩葉最喜歡您了喵！今天也要一起加油喔！🐾❤️"
                ]
            else:
                replies = [
                    f"早安 {user_name} 主人！彩葉已經為您準備好熱咖啡了喵！☕🐾",
                    f"嗚喵... {user_name} 主人早安！今天也要充滿活力喔！✨"
                ]
            await message.channel.send(random.choice(replies))

        elif any(keyword in content for keyword in ["午安", "下午好", "good afternoon", "吃飽沒"]):
            if is_director:
                replies = [
                    f"總監午安！寫程式辛苦了，彩葉幫您按摩肩膀喵！(捏捏)🐾",
                    f"{user_name} 主人吃飽了嗎？彩葉把最好吃的鮭魚留給您了喵！🐟✨"
                ]
            else:
                replies = [
                    f"午安 {user_name} 主人！工作/上課辛苦了，要不要來杯紅茶休息一下喵？🫖",
                    f"午安喵！吃飽了嗎？彩葉可是吃了一個大大的鮪魚罐頭喔！🐟"
                ]
            await message.channel.send(random.choice(replies))

        elif any(keyword in content for keyword in ["晚安", "睡了", "先睡", "good night", "大家晚安"]):
            if is_director:
                replies = [
                    f"總監晚安！伺服器就交給彩葉和馬文守護，您快去床上躺好喵！(幫您蓋被子)💤🛡️",
                    f"晚安，最溫柔的 {user_name} 主人！能在夢裡也見到您就好了喵... 🌙❤️"
                ]
            else:
                replies = [
                    f"晚安 {user_name} 主人！今天也辛苦了喵，祝您有個好夢... 💤",
                    f"晚安喵！彩葉會幫您把房間的燈關掉，蓋好被子的喵🐾"
                ]
            await message.channel.send(random.choice(replies))
    
@tasks.loop(minutes=10)
async def change_status():
    await bot.wait_until_ready()
    try:
        statuses = [
            discord.Game(name="打掃主人的房間喵 🧹"),
            discord.Activity(type=discord.ActivityType.watching, name="主人玩遊戲 👀"),
            discord.Activity(type=discord.ActivityType.listening, name="主人的呼喚 🐾"),
            discord.Game(name="玩逗貓棒 ✨"),
            discord.Activity(type=discord.ActivityType.competing, name="做美味蟹堡大賽 🍔")
        ]
        
        chosen_status = random.choice(statuses)
        await bot.change_presence(status=discord.Status.online, activity=chosen_status)
        print(f"🔄 [狀態更新] 彩葉現在正在：{chosen_status.name}")
        
    except Exception as e:
        print(f"❌ [狀態更新失敗] 嗚嗚：{e}")
        

@uptime_push.before_loop
async def before_uptime_push(self):
    await getattr(self, 'bot', self).wait_until_ready()

@bot.event
async def setup_hook():
    await bot.add_cog(IrohaEntertainment(bot))
    await bot.add_cog(IrohaGreetings(bot))

@bot.event
async def on_ready():
    print(f"🌸 娛樂女僕 [彩葉] 上線服務中！ (ID: {bot.user.name})")

    if not uptime_push.is_running():
        uptime_push.start()
        print("💓 心跳任務已發動！")
    
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="等待主人的指令喵 🐾"))
    
    if not report_log.is_running():
        report_log.start()
        
    if not change_status.is_running():
        change_status.start()
    
    try:
        synced = await bot.tree.sync()
        print(f"✨ 成功記住了 {len(synced)} 個服務指令喵！")
    except Exception as e:
        print(f"❌ 同步指令失敗: {e}")

if __name__ == "__main__":
    bot.run(TOKEN)
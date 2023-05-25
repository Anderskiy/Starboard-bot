import disnake
from disnake.ext import commands
import json
import pytz
import io

sparkles_emoji = ['sparkles', '✨'] # Сюда записать название ембодзи и само емодзи, на которое будет реагировать бот
# Отрытие бд
starboard_file = 'starboard_messages.json'
try:
    with open(starboard_file, 'r') as file:
        starboard_messages = json.load(file)
except FileNotFoundError:
    starboard_messages = {}

class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.starboard_channel_id = 1111184215778795530  # Замените на ID вашего канала Starboard

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if payload.emoji.name in sparkles_emoji:
            starboard_channel = guild.get_channel(self.starboard_channel_id)
            reactions = [reaction for reaction in message.reactions if str(reaction.emoji) in sparkles_emoji]
            total_reactions = sum([reaction.count for reaction in reactions])

            if total_reactions >= 20: # Реакция, на которую будет создаваться новый пост
                if str(message.id) in starboard_messages:
                    # Обновление существующего эмбеда
                    starboard_message_id = starboard_messages[str(message.id)]
                    starboard_message = await starboard_channel.fetch_message(starboard_message_id)
                    starboard_embed = starboard_message.embeds[0]
                    sparkles_reaction = next((reaction for reaction in reactions if str(reaction.emoji) in sparkles_emoji),
                                          None)
                    if sparkles_reaction:
                        sparkles_count = sparkles_reaction.count
                        starboard_embed.set_field_at(0, name='Реакций:', value=f"{sparkles_count}  ✨")
                    await starboard_message.edit(embed=starboard_embed)
                else:
                    if message.attachments: # Если есть файл
                        file = message.attachments[0]
                        file_url = message.attachments[0].url
                        if file.content_type.startswith('video/'): # Если есть видео
                            # Создание нового эмбеда
                            starboard_embed = disnake.Embed(color=0xE1AE53)

                            starboard_embed.set_author(name=message.author.display_name,
                                                       icon_url=message.author.display_avatar.url)

                            starboard_embed.description = message.content

                            clown_reaction = next(
                                (reaction for reaction in reactions if str(reaction.emoji) in sparkles_emoji),
                                None)

                            if message.attachments:
                                file_url = message.attachments[0].url
                                starboard_embed.set_image(url=file_url)
                                starboard_embed.add_field(name="Видео выше:", value="", inline=False)

                            if clown_reaction:
                                sparkles_count = clown_reaction.count
                                starboard_embed.add_field(name='Реакций:', value=f"{sparkles_count}  ✨")

                            # Преобразование времени в формат МСК
                            moscow_tz = pytz.timezone('Europe/Moscow')
                            timestamp = message.created_at.astimezone(moscow_tz)
                            formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')

                            starboard_embed.set_footer(text=f'В: #{channel.name} • {formatted_time}')

                            # Создание кнопки с ссылкой на сообщение
                            view = disnake.ui.View()
                            message_link = f'https://discord.com/channels/{guild.id}/{channel.id}/{message.id}'
                            button = disnake.ui.Button(label='Ссылка на сообщение', url=message_link, row=0)
                            view.add_item(button)

                            file_data = io.BytesIO()
                            await file.save(file_data)

                            file_data.seek(0)

                            # Отправка видеофайла
                            starboard_message = await starboard_channel.send(file=disnake.File(file_data, filename=file.filename),
                                                             embed=starboard_embed, view=view)

                            file_data.close()

                            # Сохранение ID сообщения и соответствующего ембеда
                            starboard_messages[str(message.id)] = starboard_message.id
                            save_starboard_messages()
                        else:
                            starboard_embed = disnake.Embed(color=0xE1AE53)

                            starboard_embed.set_author(name=message.author.display_name,
                                                       icon_url=message.author.display_avatar.url)

                            starboard_embed.description = message.content

                            clown_reaction = next(
                                (reaction for reaction in reactions if str(reaction.emoji) in sparkles_emoji),
                                None)

                            starboard_embed.set_image(url=file_url)

                            if clown_reaction:
                                sparkles_count = clown_reaction.count
                                starboard_embed.add_field(name='Реакций:', value=f"{sparkles_count}  ✨")

                            # Преобразование времени в формат МСК
                            moscow_tz = pytz.timezone('Europe/Moscow')
                            timestamp = message.created_at.astimezone(moscow_tz)
                            formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')

                            starboard_embed.set_footer(text=f'В: #{channel.name} • {formatted_time}')

                            # Создание кнопки с ссылкой на сообщение
                            view = disnake.ui.View()
                            message_link = f'https://discord.com/channels/{guild.id}/{channel.id}/{message.id}'
                            button = disnake.ui.Button(label='Ссылка на сообщение', url=message_link, row=0)
                            view.add_item(button)

                            starboard_message = await starboard_channel.send(embed=starboard_embed, view=view)

                            # Сохранение ID сообщения и соответствующего ембеда
                            starboard_messages[str(message.id)] = starboard_message.id
                            save_starboard_messages()
                    else:
                        starboard_embed = disnake.Embed(color=0xE1AE53)

                        starboard_embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)

                        starboard_embed.description = message.content

                        clown_reaction = next((reaction for reaction in reactions if str(reaction.emoji) in sparkles_emoji),
                                          None)

                        if clown_reaction:
                                sparkles_count = clown_reaction.count
                                starboard_embed.add_field(name='Реакций:', value=f"{sparkles_count}  ✨")

                        # Преобразование времени в формат МСК
                        moscow_tz = pytz.timezone('Europe/Moscow')
                        timestamp = message.created_at.astimezone(moscow_tz)
                        formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')

                        starboard_embed.set_footer(text=f'В: #{channel.name} • {formatted_time}')

                        # Создание кнопки с ссылкой на сообщение
                        view = disnake.ui.View()
                        message_link = f'https://discord.com/channels/{guild.id}/{channel.id}/{message.id}'
                        button = disnake.ui.Button(label='Ссылка на сообщение', url=message_link, row=0)
                        view.add_item(button)


                        starboard_message = await starboard_channel.send(embed=starboard_embed, view=view)

                        # Сохранение ID сообщения и соответствующего ембеда
                        starboard_messages[str(message.id)] = starboard_message.id
                        save_starboard_messages()

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if payload.emoji.name in sparkles_emoji:
            starboard_channel = guild.get_channel(self.starboard_channel_id)
            reactions = [reaction for reaction in message.reactions if str(reaction.emoji) in sparkles_emoji]
            total_reactions = sum([reaction.count for reaction in reactions])

            if total_reactions >= 18: # Реакция, на которую будет создаваться новый пост
                if str(message.id) in starboard_messages:
                    # Обновление эмбеда, если реакция была удалена, но общее количество реакций все еще больше 20
                    starboard_message_id = starboard_messages[str(message.id)]
                    starboard_message = await starboard_channel.fetch_message(starboard_message_id)
                    starboard_embed = starboard_message.embeds[0]
                    clown_reaction = next((reaction for reaction in reactions if str(reaction.emoji) in sparkles_emoji),
                                          None)
                    if clown_reaction:
                        sparkles_count = clown_reaction.count
                        starboard_embed.set_field_at(0, name='Реакций:', value=f"{sparkles_count}  ✨")
                    await starboard_message.edit(embed=starboard_embed)
            else:
                if str(message.id) in starboard_messages:
                    # Удаление эмбеда, если реакции на сообщении меньше 3
                    starboard_message_id = starboard_messages[str(message.id)]
                    starboard_message = await starboard_channel.fetch_message(starboard_message_id)
                    await starboard_message.delete()
                    del starboard_messages[str(message.id)]
                    save_starboard_messages()

# Сохранение бд
def save_starboard_messages():
    with open(starboard_file, 'w') as file:
        json.dump(starboard_messages, file)

# Коги
def setup(bot):
    bot.add_cog(Starboard(bot))

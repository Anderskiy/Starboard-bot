import disnake
from disnake.ext import commands

import os
import pytz
import io
from datetime import datetime

from db import *
from config import *

from dotenv import load_dotenv

load_dotenv()


intents = disnake.Intents.default()
intents.reactions = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix=".", help_command=None, intents=intents)


@bot.event
async def on_raw_reaction_add(payload: disnake.RawReactionActionEvent):
    if payload.emoji.name not in list_emoji:
        return

    guild = bot.get_guild(payload.guild_id)
    channel = guild.get_channel(payload.channel_id)
    if not channel:
        return
    message = disnake.utils.get(bot.cached_messages, id=payload.message_id)
    if not message:
        message = await channel.fetch_message(payload.message_id)

    if payload.emoji.name in list_emoji:
        starboard_channel = guild.get_channel(starboard_channel_id)
        reactions = get_reactions(message)
        total_reactions = sum(reaction.count for reaction in reactions)

        if total_reactions >= starboard_reaction_post:
            starboard_message_id = get_starboard_message_id(message.id)
            if starboard_message_id:
                starboard_message = await starboard_channel.fetch_message(starboard_message_id)
                starboard_embed = starboard_message.embeds[0]
                sparkles_reaction = next((reaction for reaction in reactions if reaction.emoji.name in list_emoji),
                                         None)
                if sparkles_reaction:
                    sparkles_count = sparkles_reaction.count
                    is_video = False

                    for attachment in message.attachments:
                        if attachment.filename.endswith('.mp4') or attachment.filename.endswith('.mov'):
                            is_video = True
                            starboard_embed.set_field_at(0, name='Видео выше:', value="", inline=False)
                            starboard_embed.set_field_at(1, name='Реакций:', value=f"{sparkles_count}  {emoji}")
                    if not is_video:
                        starboard_embed.set_field_at(0, name='Реакций:', value=f"{sparkles_count}  {emoji}")
                await starboard_message.edit(embed=starboard_embed)
            else:
                starboard_embed = disnake.Embed(color=embed_color, timestamp=get_time(message))
                starboard_embed.set_author(name=message.author.display_name,
                                           icon_url=message.author.display_avatar.url)
                starboard_embed.description = message.content

                sparkles_reaction = next(
                    (reaction for reaction in reactions if reaction.emoji.name in list_emoji), None)

                if sparkles_reaction:
                    starboard_embed.add_field(name='Реакций:', value=f"{sparkles_reaction.count}  {emoji}")

                starboard_embed.set_footer(text=f'В: #{channel.name}')

                view = disnake.ui.View()
                message_link = f'https://discord.com/channels/{guild.id}/{channel.id}/{message.id}'
                button = disnake.ui.Button(label='Ссылка на сообщение', url=message_link, row=0)
                view.add_item(button)

                if message.attachments:
                    _file = message.attachments[0]
                    file_url = message.attachments[0].url

                    if _file.content_type.startswith('video/'):
                        starboard_embed.set_image(url=message.attachments[0].url)
                        starboard_embed.add_field(name="Видео выше:", value="", inline=False)

                        file_data = io.BytesIO()
                        await _file.save(file_data)

                        file_data.seek(0)

                        starboard_message = await starboard_channel.send(
                            file=disnake.File(file_data, filename=_file.filename),
                            embed=starboard_embed, view=view)

                        file_data.close()
                    else:
                        starboard_embed.set_image(url=file_url)

                        starboard_message = await starboard_channel.send(embed=starboard_embed, view=view)
                else:
                    starboard_message = await starboard_channel.send(embed=starboard_embed, view=view)

                save_starboard_message(message.id, starboard_message.id)


@bot.event
async def on_raw_reaction_remove(payload: disnake.RawReactionActionEvent):
    if payload.emoji.name not in list_emoji:
        return

    guild = bot.get_guild(payload.guild_id)
    channel = guild.get_channel(payload.channel_id)
    if not channel:
        return
    message = disnake.utils.get(bot.cached_messages, id=payload.message_id)
    if not message:
        message = await channel.fetch_message(payload.message_id)

    if payload.emoji.name in list_emoji:
        starboard_channel = guild.get_channel(starboard_channel_id)
        reactions = get_reactions(message)
        total_reactions = sum(reaction.count for reaction in reactions)

        if total_reactions >= starboard_reaction_post:  # Реакция, на которую будет создаваться новый пост
            starboard_message_id = get_starboard_message_id(message.id)
            if starboard_message_id:
                # Обновление эмбеда, если реакция была удалена, но общее количество реакций все еще больше starboard_reaction_post
                starboard_message = await starboard_channel.fetch_message(starboard_message_id)
                starboard_embed = starboard_message.embeds[0]
                sparkles_reaction = next((reaction for reaction in reactions if reaction.emoji.name in list_emoji),
                                         None)
                if sparkles_reaction:
                    sparkles_count = sparkles_reaction.count
                    is_video = False

                    for attachment in message.attachments:
                        if attachment.filename.endswith('.mp4') or attachment.filename.endswith('.mov'):
                            is_video = True
                            starboard_embed.set_field_at(0, name='Видео выше:', value="", inline=False)
                            starboard_embed.set_field_at(1, name='Реакций:', value=f"{sparkles_count}  {emoji}")
                    if not is_video:
                        starboard_embed.set_field_at(0, name='Реакций:', value=f"{sparkles_count}  {emoji}")
                await starboard_message.edit(embed=starboard_embed)
        else:
            starboard_message_id = get_starboard_message_id(message.id)
            if starboard_message_id:
                # Удаление эмбеда, если реакции на сообщении меньше starboard_reaction_post
                starboard_message = await starboard_channel.fetch_message(starboard_message_id)
                await starboard_message.delete()
                delete_starboard_message(message.id)


def get_reactions(message: disnake.Message) -> list[disnake.Reaction]:
    reactions = []
    for reaction in message.reactions:
        try:
            if reaction.emoji.name in list_emoji:
                reactions.append(reaction)
        except AttributeError:
            pass
    return reactions

def get_time(message: disnake.Message) -> datetime:
    moscow_tz = pytz.timezone('Europe/Moscow')
    timestamp = message.created_at.astimezone(moscow_tz)
    return timestamp


if __name__ == "__main__":
    bot.run(os.getenv('TOKEN'))

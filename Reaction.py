# Coded by Y4sperMaglot

from .. import utils, loader
from telethon import types



emojis = ['👍', '👎', '❤️', '🔥', '🥰', '👏', '😁', '🤔', '🤯', '😱', '🤬', '😢', '🎉', '🤩', '🤮', '💩']


@loader.tds
class AutomaticReactionMod(loader.Module):
	"""Автоматически ставит реакцию на сообщение"""
	strings = {'name': 'AutomaticReaction'}

	async def client_ready(self, client, db):
		self.client = client
		self.db = db


	async def reactionlistcmd(self, message):
		""".reactionlist чтобы посмотреть список пользователей"""
		reactions = self.db.get("reaction", "reactions")
		if reactions is None:
			return await message.edit("<b>Список пуст.</b>")
		text = ""
		for reaction in reactions:
			text += f"""<b>👤 Пользователь: <a href='tg://user?id={reaction["user_id"]}'>{reaction["user_id"]}</a>
💬 Чат: <code>{reaction["chat_id"]}</code>
🌀 Реакция: <code>{reaction["emoji"]}</code></b>
"""
		await message.delete()
		await self.client.send_message(message.to_id, text)

	async def reactioncmd(self, message):
		"""<.reaction чтобы включить> <.reaction off чтобы выключить>"""
		self.db.set("reaction", "status", True) if 'on' in utils.get_args_raw(message) else self.db.set("reaction", "status", False)
		await message.edit("<b>Модуль Reaction включён</b>") if 'on' in utils.get_args_raw(message) else await message.edit("<b>Модуль Reaction выключен</b>")

	async def reactionclscmd(self, message):
		""".reactioncls чтобы очистить список"""
		self.db.set("reaction", "reactions", None)
		await message.edit("<b>Список очищен</b>")

	async def reactionreplycmd(self, message):
		""".reactionreply <reaction> и реплай на сообщение человека"""
		emoji = utils.get_args_raw(message)
		if emoji not in emojis:
			return await message.edit("<b>Такой реакции нет.</b>")
		user_id = (await message.get_reply_message()).from_id
		try:
			chat_id = message.peer_id.user_id if message.chat is None else message.chat.id
		except:
			chat_id = message.peer_id.chat_id if message.chat is None else message.chat.id
		reaction = {"emoji": emoji, "user_id": user_id, "chat_id": chat_id}

		reactions = self.db.get("reaction", "reactions")
		if reactions is None:
			reactions = []
		reactions.append(reaction)
		self.db.set("reaction", "reactions", reactions)
		await message.edit(f"<b>Готово, теперь на сообщения пользователя <a href='tg://user?id={user_id}'>{(await self.client.get_entity(user_id)).first_name}</a> будет ставиться реакция {emoji}</b>")

	async def reactionsetcmd(self, message):
		""".reactionset <chat_id> <username/id> <reaction> в указанном порядке"""
		args = (utils.get_args_raw(message)).split()
		chat_id = int(args[0])
		user_id = args[1] if "@" not in args[1] else (await self.client.get_entity(args[1])).id
		emoji = args[2]
		if emoji not in emojis:
			return await message.edit("<b>Такой реакции нет.</b>")
		reaction = {"emoji": emoji, "user_id": user_id, "chat_id": chat_id}

		reactions = self.db.get("reaction", "reactions")
		if reactions is None:
			reactions = []
		reactions.append(reaction)
		self.db.set("reaction", "reactions", reactions)
		await message.edit(f"<b>Готово, теперь на сообщения пользователя <a href='tg://user?id={user_id}'>{user_id}</a> в чате с id {str(chat_id)} будет ставиться реакция {emoji}</b>")

	async def reactiondelcmd(self, message):
		""".reactiondel <chat_id> <username/id> в указанном порядке"""
		args = (utils.get_args_raw(message)).split()
		chat_id = args[0]
		user_id = args[1] if "@" not in args[1] else (await self.client.get_entity(args[1])).id

		reactions = self.db.get("reaction", "reactions")
		if reactions is None:
			return await message.edit("<b>Список пуст.</b>")

		for reaction in reactions:
			if all([reaction["chat_id"] == chat_id, reaction["user_id"] == user_id]):
				reactions.remove(reaction)
		self.db.set("reaction", "reactions", reactions.append(reaction))
		await message.edit(f"<b>Готово, пользователь <a href='tg://user?id={user_id}'>{user_id}</a> удалён из списка.</b>")

	async def watcher(self, m: types.Message):
		if self.db.get("reaction", "status"):
			reactions = self.db.get("reaction", "reactions")
			for r in reactions:
				if m.chat is None:
					try:
						if m.from_id == r["user_id"] and m.peer_id.user_id == r["chat_id"]:
							await self.client.send_reaction(message=m.id, reaction=(r["emoji"]).encode("utf-8"), entity=m.from_id)
					except:
						if m.from_id == r["user_id"] and m.peer_id.chat_id == r["chat_id"]:
							await self.client.send_reaction(message=m.id, reaction=(r["emoji"]).encode("utf-8"), entity=m.peer_id)
				else:
					if m.from_id == r["user_id"] and m.chat.id == r["chat_id"]:
						await self.client.send_reaction(message=m.id, reaction=(r["emoji"]).encode("utf-8"), entity=m.peer_id)
			
			
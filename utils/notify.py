import os
import re
import smtplib
from email.mime.text import MIMEText
from typing import Literal

import httpx
import traceback


class NotificationKit:
	def __init__(self):
		self.email_user: str = os.getenv('EMAIL_USER', '')
		self.email_pass: str = os.getenv('EMAIL_PASS', '')
		self.email_to: str = os.getenv('EMAIL_TO', '')
		self.smtp_server: str = os.getenv('CUSTOM_SMTP_SERVER', '')
		self.pushplus_token = os.getenv('PUSHPLUS_TOKEN')
		self.server_push_key = os.getenv('SERVERPUSHKEY')
		self.dingding_webhook = os.getenv('DINGDING_WEBHOOK')
		self.feishu_webhook = os.getenv('FEISHU_WEBHOOK')
		self.weixin_webhook = os.getenv('WEIXIN_WEBHOOK')
		self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
		self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')

	def send_email(self, title: str, content: str, msg_type: Literal['text', 'html'] = 'text'):
		if not self.email_user or not self.email_pass or not self.email_to:
			raise ValueError('Email configuration not set')

		# MIMEText 需要 'plain' 或 'html'，而不是 'text'
		mime_subtype = 'plain' if msg_type == 'text' else 'html'
		msg = MIMEText(content, mime_subtype, 'utf-8')
		msg['From'] = f'AnyRouter Assistant <{self.email_user}>'
		msg['To'] = self.email_to
		msg['Subject'] = title

		smtp_server = self.smtp_server if self.smtp_server else f'smtp.{self.email_user.split("@")[1]}'
		with smtplib.SMTP_SSL(smtp_server, 465) as server:
			server.login(self.email_user, self.email_pass)
			server.send_message(msg)

	def send_pushplus(self, title: str, content: str):
		if not self.pushplus_token:
			raise ValueError('PushPlus Token not configured')

		data = {'token': self.pushplus_token, 'title': title, 'content': content, 'template': 'html'}
		with httpx.Client(timeout=30.0) as client:
			client.post('http://www.pushplus.plus/send', json=data)

	def send_serverPush(self, title: str, content: str):
		if not self.server_push_key:
			raise ValueError('Server Push key not configured')

		data = {'title': title, 'desp': content}
		with httpx.Client(timeout=30.0) as client:
			client.post(f'https://sctapi.ftqq.com/{self.server_push_key}.send', json=data)

	def send_dingtalk(self, title: str, content: str):
		if not self.dingding_webhook:
			raise ValueError('DingTalk Webhook not configured')

		data = {'msgtype': 'text', 'text': {'content': f'{title}\n{content}'}}
		with httpx.Client(timeout=30.0) as client:
			client.post(self.dingding_webhook, json=data)

	def send_feishu(self, title: str, content: str):
		if not self.feishu_webhook:
			raise ValueError('Feishu Webhook not configured')

		data = {
			'msg_type': 'interactive',
			'card': {
				'elements': [{'tag': 'markdown', 'content': content, 'text_align': 'left'}],
				'header': {'template': 'blue', 'title': {'content': title, 'tag': 'plain_text'}},
			},
		}
		with httpx.Client(timeout=30.0) as client:
			client.post(self.feishu_webhook, json=data)

	def send_wecom(self, title: str, content: str):
		if not self.weixin_webhook:
			raise ValueError('WeChat Work Webhook not configured')

		data = {'msgtype': 'text', 'text': {'content': f'{title}\n{content}'}}
		with httpx.Client(timeout=30.0) as client:
			client.post(self.weixin_webhook, json=data)

	def send_telegram(self, title: str, content: str):
		if not self.telegram_bot_token or not self.telegram_chat_id:
			raise ValueError('Telegram Bot Token or Chat ID not configured')

		# 支援表格格式：未設定時自動偵測是否包含餘額資訊
		fmt = os.getenv('TELEGRAM_FORMAT', '').lower()
		message = f'<b>{title}</b>\n\n{content}'
		auto_table = any(
			line.strip().startswith('[BALANCE]') or re.search(r'Current balance: \$[0-9.]+, Used: \$[0-9.]+', line)
			for line in content.splitlines()
		)
		use_table = True if fmt == 'table' else False if fmt == 'plain' else auto_table
		if use_table:
				lines = content.splitlines()
				rows: list[tuple[str, str, str]] = []  # (account, balance, used)
				consumed_balance_line: set[int] = set()
				for i, line in enumerate(lines):
					line = line.strip()
					if line.startswith('[SUCCESS]') or line.startswith('[FAIL]') or line.startswith('[BALANCE]'):
						# 解析帳號名稱（去除前導標籤）
						try:
							status_end = line.index(']')
							account = line[status_end + 1 :].strip()
						except Exception:
							account = line

						# 嘗試解析下一行的餘額與用量
						bal = '-'
						used = '-'
						if i + 1 < len(lines):
							m = re.search(r'Current balance: \$([0-9.]+), Used: \$([0-9.]+)', lines[i + 1])
							if m:
								bal = m.group(1)
								used = m.group(2)
								consumed_balance_line.add(i + 1)

						rows.append((account, bal, used))

				# 建立非表格文字：保留其他行（包含 [TIME]、統計等），排除帳號行與已消耗的餘額行
				non_table_lines: list[str] = []
				for j, ln in enumerate(lines):
					if j in consumed_balance_line:
						continue
					if ln.strip().startswith('[SUCCESS]') or ln.strip().startswith('[FAIL]') or ln.strip().startswith('[BALANCE]'):
						continue
					non_table_lines.append(ln)
				non_table_text = '\n'.join(non_table_lines).strip()

				if rows:
					headers = ('帳號', '餘額($)', '已用($)')
					widths = [len(h) for h in headers]
					for acc, bal, usd in rows:
						widths[0] = max(widths[0], len(str(acc)))
						widths[1] = max(widths[1], len(str(bal)))
						widths[2] = max(widths[2], len(str(usd)))

					def fmt(row: tuple[str, str, str]) -> str:
						return (
							str(row[0]).ljust(widths[0])
							+ '  '
							+ str(row[1]).rjust(widths[1])
							+ '  '
							+ str(row[2]).rjust(widths[2])
						)

					head = fmt(headers)  # type: ignore[arg-type]
					body = '\n'.join(fmt(r) for r in rows)
					if non_table_text:
						message = f'<b>{title}</b>\n\n{non_table_text}\n\n<pre>{head}\n{body}</pre>'
					else:
						message = f'<b>{title}</b>\n\n<pre>{head}\n{body}</pre>'
		data = {'chat_id': self.telegram_chat_id, 'text': message, 'parse_mode': 'HTML'}
		url = f'https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage'
		with httpx.Client(timeout=30.0) as client:
			resp = client.post(url, json=data)
			# 詳細錯誤輸出：HTTP 狀態與 API 錯誤描述
			if resp.status_code != 200:
				api_desc = ''
				try:
					payload = resp.json()
					api_desc = f" error_code={payload.get('error_code')}, description={payload.get('description')}"
				except Exception:
					api_desc = f' body={resp.text[:200]}'
				raise RuntimeError(f'Telegram HTTP {resp.status_code}.{api_desc}')

			try:
				payload = resp.json()
			except Exception:
				raise RuntimeError(f'Telegram invalid JSON response: {resp.text[:200]}')

			if not payload.get('ok', True):
				raise RuntimeError(
					f"Telegram API error: error_code={payload.get('error_code')}, description={payload.get('description')}"
				)

	def push_message(self, title: str, content: str, msg_type: Literal['text', 'html'] = 'text'):
		notifications = [
			('Email', lambda: self.send_email(title, content, msg_type)),
			('PushPlus', lambda: self.send_pushplus(title, content)),
			('Server Push', lambda: self.send_serverPush(title, content)),
			('DingTalk', lambda: self.send_dingtalk(title, content)),
			('Feishu', lambda: self.send_feishu(title, content)),
			('WeChat Work', lambda: self.send_wecom(title, content)),
			('Telegram', lambda: self.send_telegram(title, content)),
		]

		for name, func in notifications:
			try:
				func()
				print(f'[{name}]: Message push successful!')
			except Exception as e:
				debug = os.getenv('NOTIFY_DEBUG', '').lower() == 'true'
				msg = f'[{name}]: Message push failed! Reason: {e.__class__.__name__}: {str(e)}'
				if debug:
					msg += f"\n{traceback.format_exc()}"
				print(msg)


notify = NotificationKit()

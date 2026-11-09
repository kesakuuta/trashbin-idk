# meta developer: @GemModules

import logging
import aiohttp
from telethon.tl.types import Message
from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class USADebtMod(loader.Module):
    """Модуль для получения актуального государственного долга США"""

    strings = {
        "name": "USADebt",
        "loading": "<b>🔄 Загрузка данных от Минфина США...</b>",
        "error": "<b>❌ Не удалось получить данные о госдолге США. Попробуйте позже.</b>",
        "result": (
            "<b>🇺🇸 Государственный долг США</b>\n\n"
            "<b>Сумма:</b> <code>${debt:,.2f}</code>\n"
            "<b>Дата фиксации:</b> <code>{date}</code>"
        ),
    }

    @loader.command()
    async def usa(self, message: Message):
        """Показать текущий госдолг США"""
        message = await utils.answer(message, self.strings("loading"))

        url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/debt_to_penny?sort=-record_date&page[size]=1"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status != 200:
                        await utils.answer(message, self.strings("error"))
                        return

                    data = await response.json()
                    
                    if not data.get("data"):
                        await utils.answer(message, self.strings("error"))
                        return

                    latest_record = data["data"][0]
                    debt_amount = float(latest_record["tot_pub_debt_out_amt"])
                    record_date = latest_record["record_date"]

                    formatted_text = self.strings("result").format(
                        debt=debt_amount,
                        date=record_date
                    )
                    
                    await utils.answer(message, formatted_text)

        except Exception as e:
            logger.error(f"Error fetching USA debt: {e}")
            await utils.answer(message, self.strings("error"))

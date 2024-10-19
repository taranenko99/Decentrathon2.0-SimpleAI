# Aiogram
from aiogram import Router, F

# Third-Party
import asyncio

# local
from src.v1.states import Master, Patient
from src.v1.mixins import MessageMixin, CallbackMixin
from src.v1.utils.master import update_patient, make_chat, check_patient, check_doctor
from .doctor import Alarm


router = Router(name="Patient Router")


class StartDialog(MessageMixin):
    async def handle(self):
        self.progress_func()
        await self.fsm.set_state(state=Patient.dialog)
        await self.make_response(
            text="Здравствуйте! Как ваше самочувствие?"
        )


@router.callback_query(Master.select, F.data == "patient")
class PatType(CallbackMixin):
    async def handle(self):
        self.progress_func()
        await self.answer_to_callback()
        await self.fsm.set_state(state=Master.pat_number)
        await self.make_response(text="Пожалуйста введите свой ИИН")


@router.message(Master.pat_number)
class UpdatePatient(MessageMixin):
    async def handle(self):
        self.progress_func()
        if len(self.event.text) != 12:
            await self.make_response(
                text="ИИН должен содержать 12 цифр!"
            )
            return
        updated = await update_patient(data={
            "individual_number": self.event.text,
            "telegram_id": self.chat_id
        })
        if not updated:
            await self.make_response(
                text="Чтото пошло не так"
            )
            return
        await self.make_response(
            text="Спасибо за регистрацию, я буду связываться с вами ежедневно для мониторинга вашего состояния, вы так же можете использовать команду /start если вам нужна консультация!"
        )
        await asyncio.sleep(60)
        help_func = StartDialog(event=self.event)
        await help_func.handle()


@router.message(Patient.dialog)
class Dialog(MessageMixin):
    async def handle(self):
        self.progress_func()
        chat = await make_chat(
            telegram_id=self.chat_id, message=self.event.text
        )
        if not chat:
            await self.make_response(
                text="Извините, временные проблемы с сервером!"
            )
            return
        trigger = chat.get("trigger")
        text = chat.get("bot_message")
        if trigger == 0:
            await self.make_response(text=text)
            return
        elif trigger == 1:
            me = await check_patient(telegram_id=self.chat_id)
            iin = me.get("individual_number")
            doctor_tele_id = me["doctor"]["telegram_id"]
            help_func = Alarm(event=self.event)
            await help_func.handle(patient_num=iin, doc_tele_id=doctor_tele_id)
            await self.fsm.clear()
            await self.make_response(
                text="""C вами скоро свяжется акушерка или врач, но вы можете ответить на их звонок из машины скорой помощи.
у вас обнаружены тревожные признаки и вам надлежит незамедлительно вызовите скорую помощь!"""
            )
        elif trigger == 2:
            await self.fsm.clear()
            await self.make_response(text="Спасибо за обратную связь, помните, вы всегда можете использовать команду /start если нужна консультация!")

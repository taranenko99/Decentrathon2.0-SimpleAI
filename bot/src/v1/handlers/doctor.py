# Aiogram
from aiogram import Router, F

# Python
import os

# local
from src.v1.states import Master, Doctor
from src.v1.mixins import MessageMixin, CallbackMixin
from src.v1.utils.master import create_doctor, create_patient, send_test
from src.settings.base import bot, VOLUME


router = Router(name="Doctor Router")


class Alarm(MessageMixin):
    async def handle(self, patient_num: str, doc_tele_id: int):
        self.progress_func()
        await bot.send_message(
            chat_id=doc_tele_id, text=f"Тревога! У пациента {patient_num} тревожные признаки! Срочно свяжитесь с пациентом!"
        )


@router.callback_query(Master.select, F.data == "doctor")
class DocType(CallbackMixin):
    async def handle(self):
        self.progress_func()
        await self.answer_to_callback()
        await self.fsm.set_state(state=Master.doc_number)
        await self.make_response(text="Пожалуйста введите свой ИИН")


@router.message(Master.doc_number)
class CreateDoctor(MessageMixin):
    async def handle(self):
        self.progress_func()
        if len(self.event.text) != 12:
            await self.make_response(
                text="ИИН должен содержать 12 цифр!"
            )
            return
        created = await create_doctor(data={
            "individual_number": self.event.text,
            "telegram_id": self.chat_id
        })
        if not created:
            await self.make_response(
                text="Невозможно создать пользователя"
            )
            return
        await self.fsm.clear()
        await self.make_response(
            text="""Регистрация прошла успешно! 
            \nВы можете использовать команды в меню чтобы добавлять пациентов и их анализы!"""
        )


@router.message(Doctor.add_patient)
class JoinPatient(MessageMixin):
    async def handle(self):
        self.progress_func()
        if len(self.event.text) != 12:
            await self.make_response(
                text="ИИН должен содержать 12 цифр!"
            )
            return
        data = await self.fsm.get_data()
        doctor = data.get("user")
        created = await create_patient(data={
            "doctor_id": doctor.get("id"),
            "individual_number": self.event.text
        })
        if not created:
            await self.make_response(
                text="Что-то пошло не так"
            )
            return
        await self.fsm.clear()
        await self.make_response(text="Пациент добавлен!")


@router.callback_query(Doctor.add_tests)
class SelectPatient(CallbackMixin):
    async def handle(self):
        self.progress_func()
        await self.answer_to_callback()
        await self.fsm.update_data(data={
            "patient_id": int(self.event.data)
        })
        await self.fsm.set_state(state=Doctor.wait_doc)
        await self.make_response(text="Отправьте изображение или документ")


@router.message(Doctor.wait_doc)
class AddPhoto(MessageMixin):
    async def handle(self):
        self.progress_func()
        try:
            photo = self.event.document.file_id
            filename = self.event.document.file_name
        except:
            await self.make_response(text="Я же сказал фото или документ!")
            return
        data = await self.fsm.get_data()
        patient_id = data.get("patient_id")
        photo_file = await bot.get_file(file_id=photo)
        filepath = os.path.join(VOLUME, filename)
        await bot.download_file(file_path=photo_file.file_path, destination=filepath)
        answer = await send_test(filepath=filepath, patient_id=patient_id, filename=filename)
        if not answer:
            await self.make_response(text="Что-то пошло не так, отправьте еще раз")
            return
        await self.fsm.clear()
        await self.make_response(text="Анализ успешно загружен!")

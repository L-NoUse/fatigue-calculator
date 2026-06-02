import csv
import json
import os
from datetime import datetime
from uuid import uuid4


class DataManager:
    USERS_FILE = "users.json"
    RECORDS_FILE = "fatigue_data.csv"

    FIELD_NAMES = [
        "record_id",
        "user_id",
        "date",
        "sleep_hours",
        "sleep_quality",
        "work_hours",
        "screen_hours",
        "water_ml",
        "exercise_minutes",
        "exercise_intensity",
        "exercise_load",
        "mood_score",
        "body_status",
        "special_status",
        "fatigue",
        "status",
        "standard_summary",
    ]

    FLOAT_FIELDS = {"sleep_hours", "work_hours", "screen_hours", "exercise_load", "fatigue"}
    INT_FIELDS = {"water_ml", "exercise_minutes", "mood_score"}

    @classmethod
    def load_users(cls):
        if not os.path.exists(cls.USERS_FILE):
            return []
        with open(cls.USERS_FILE, encoding="utf-8") as file:
            return json.load(file)

    @classmethod
    def save_users(cls, users):
        with open(cls.USERS_FILE, "w", encoding="utf-8") as file:
            json.dump(users, file, ensure_ascii=False, indent=2)

    @classmethod
    def create_user(cls, profile):
        users = cls.load_users()
        user = {
            "user_id": str(uuid4()),
            "name": profile["name"].strip(),
            "gender": profile.get("gender", "男"),
            "age": int(profile.get("age", 18)),
            "height_cm": float(profile.get("height_cm", 170)),
            "weight_kg": float(profile.get("weight_kg", 60)),
            "activity_level": profile.get("activity_level", "普通"),
            "role": profile.get("role", "学生"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        users.append(user)
        cls.save_users(users)
        return user

    @classmethod
    def update_user(cls, profile):
        users = cls.load_users()
        for index, user in enumerate(users):
            if user["user_id"] == profile["user_id"]:
                users[index] = profile
                cls.save_users(users)
                return profile
        users.append(profile)
        cls.save_users(users)
        return profile

    @classmethod
    def save_data(cls, data):
        records = cls.load_records()
        records.append(cls._prepare_record(data))
        cls.save_records(records)

    @classmethod
    def save_records(cls, records):
        with open(cls.RECORDS_FILE, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=cls.FIELD_NAMES, extrasaction="ignore")
            writer.writeheader()
            for record in records:
                writer.writerow(cls._prepare_record(record))

    @classmethod
    def load_data(cls):
        return cls.load_records()

    @classmethod
    def load_records(cls, user_id=None):
        if not os.path.exists(cls.RECORDS_FILE):
            return []

        with open(cls.RECORDS_FILE, newline="", encoding="utf-8-sig") as file:
            records = []
            for index, record in enumerate(csv.DictReader(file)):
                normalized = cls._normalize_record(record)
                if not normalized["record_id"]:
                    normalized["record_id"] = f"legacy-{index}"
                records.append(normalized)

        if user_id is not None:
            records = [record for record in records if record.get("user_id") == user_id]
        return records

    @classmethod
    def delete_records(cls, record_ids):
        record_ids = set(record_ids)
        records = [record for record in cls.load_records() if record.get("record_id") not in record_ids]
        deleted_count = len(record_ids)
        cls.save_records(records) if records else cls.clear_data()
        return deleted_count

    @classmethod
    def clear_data(cls, user_id=None):
        if not os.path.exists(cls.RECORDS_FILE):
            return

        if user_id is None:
            os.remove(cls.RECORDS_FILE)
            return

        records = [record for record in cls.load_records() if record.get("user_id") != user_id]
        cls.save_records(records) if records else os.remove(cls.RECORDS_FILE)

    @classmethod
    def _prepare_record(cls, data):
        record = {field: data.get(field, "") for field in cls.FIELD_NAMES}
        if not record["record_id"]:
            record["record_id"] = str(uuid4())
        if not record["date"]:
            record["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return record

    @classmethod
    def _normalize_record(cls, record):
        normalized = {field: record.get(field, "") for field in cls.FIELD_NAMES}

        if not normalized["screen_hours"] and record.get("game_hours"):
            normalized["screen_hours"] = record["game_hours"]
        if not normalized["screen_hours"]:
            normalized["screen_hours"] = 0
        if not normalized["sleep_quality"]:
            normalized["sleep_quality"] = "一般"
        if not normalized["exercise_intensity"]:
            normalized["exercise_intensity"] = "中等强度"
        if not normalized["body_status"]:
            normalized["body_status"] = "无"
        if not normalized["special_status"]:
            normalized["special_status"] = "无"

        for field in cls.FLOAT_FIELDS:
            normalized[field] = cls._to_float(normalized.get(field), 0)
        for field in cls.INT_FIELDS:
            normalized[field] = int(cls._to_float(normalized.get(field), 0))
        return normalized

    @staticmethod
    def _to_float(value, default):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

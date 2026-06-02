EXERCISE_INTENSITIES = {
    "低强度": {
        "factor": 1.0,
        "description": "散步、拉伸、轻松骑车，运动时可以轻松说话。",
    },
    "中等强度": {
        "factor": 1.8,
        "description": "快走、慢跑、健身操，运动时可以说短句但不能轻松唱歌。",
    },
    "高强度": {
        "factor": 2.5,
        "description": "跑步、球类、力量训练或 HIIT，呼吸明显加快，说话困难。",
    },
}

SLEEP_QUALITY_EFFECTS = {
    "差": 8,
    "一般": 0,
    "好": -4,
}

BODY_STATUS_EFFECTS = {
    "无": 0,
    "轻微不适": 6,
    "明显不适": 14,
}

SPECIAL_STATUS_EFFECTS = {
    "无": 0,
    "生理期": 6,
    "熬夜后": 8,
    "感冒恢复期": 10,
}


def get_age_group(age):
    age = int(age)
    if age <= 17:
        return "青少年"
    if age <= 35:
        return "青年"
    if age <= 59:
        return "中年"
    return "老年"


def get_personal_standards(profile):
    age = int(profile.get("age", 18))
    weight = float(profile.get("weight_kg", 60))
    activity_level = profile.get("activity_level", "普通")
    age_group = get_age_group(age)

    if age_group == "青少年":
        sleep_min, sleep_max = 8, 10
        exercise_load_target = 90
        work_hours_max = 8
        screen_hours_max = 2
    elif age_group == "老年":
        sleep_min, sleep_max = 7, 8
        exercise_load_target = 30
        work_hours_max = 6
        screen_hours_max = 2
    elif age_group == "中年":
        sleep_min, sleep_max = 7, 8
        exercise_load_target = 54
        work_hours_max = 8
        screen_hours_max = 2.5
    else:
        sleep_min, sleep_max = 7, 9
        exercise_load_target = 54
        work_hours_max = 8
        screen_hours_max = 3

    if activity_level == "久坐":
        exercise_load_target += 12
    elif activity_level == "活跃":
        exercise_load_target -= 8

    water_min = round(weight * 30)
    water_max = round(weight * 35)

    return {
        "age_group": age_group,
        "sleep_min": sleep_min,
        "sleep_max": sleep_max,
        "water_min": water_min,
        "water_max": water_max,
        "exercise_load_target": max(20, round(exercise_load_target)),
        "exercise_load_upper": round(exercise_load_target * 2.1),
        "work_hours_max": work_hours_max,
        "screen_hours_max": screen_hours_max,
        "gender_note": "性别用于解释特殊状态和个体差异，不作为绝对疲劳判断依据。",
    }


def calculate_exercise_load(minutes, intensity):
    factor = EXERCISE_INTENSITIES.get(intensity, EXERCISE_INTENSITIES["中等强度"])["factor"]
    return round(float(minutes) * factor, 1)


def format_standard_summary(standards):
    return (
        f"{standards['age_group']}；睡眠 {standards['sleep_min']}-{standards['sleep_max']} 小时；"
        f"饮水 {standards['water_min']}-{standards['water_max']} ml；"
        f"运动量目标 {standards['exercise_load_target']}；"
        f"工作/学习不超过 {standards['work_hours_max']} 小时；"
        f"屏幕娱乐不超过 {standards['screen_hours_max']} 小时"
    )

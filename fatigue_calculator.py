from standards import (
    BODY_STATUS_EFFECTS,
    SLEEP_QUALITY_EFFECTS,
    SPECIAL_STATUS_EFFECTS,
    calculate_exercise_load,
    get_personal_standards,
)


class FatigueCalculator:
    @staticmethod
    def calculate_fatigue(*args, profile=None, standards=None):
        if len(args) == 1 and isinstance(args[0], dict):
            return FatigueCalculator.calculate_personalized(args[0], profile, standards)
        return FatigueCalculator.calculate_legacy(*args)

    @staticmethod
    def calculate_personalized(data, profile=None, standards=None):
        standards = standards or get_personal_standards(profile or {})
        fatigue = 40

        sleep_hours = float(data["sleep_hours"])
        work_hours = float(data["work_hours"])
        screen_hours = float(data["screen_hours"])
        water_ml = int(data["water_ml"])
        exercise_minutes = int(data["exercise_minutes"])
        exercise_intensity = data.get("exercise_intensity", "中等强度")
        mood_score = int(data["mood_score"])
        sleep_quality = data.get("sleep_quality", "一般")
        body_status = data.get("body_status", "无")
        special_status = data.get("special_status", "无")

        if sleep_hours < standards["sleep_min"]:
            fatigue += (standards["sleep_min"] - sleep_hours) * 9
        elif sleep_hours <= standards["sleep_max"]:
            fatigue -= 5
        else:
            fatigue += max(0, sleep_hours - standards["sleep_max"]) * 1.5

        fatigue += SLEEP_QUALITY_EFFECTS.get(sleep_quality, 0)

        if work_hours > standards["work_hours_max"]:
            fatigue += (work_hours - standards["work_hours_max"]) * 4

        if screen_hours > standards["screen_hours_max"]:
            fatigue += (screen_hours - standards["screen_hours_max"]) * 4

        if water_ml < standards["water_min"]:
            fatigue += min(14, (standards["water_min"] - water_ml) / 120)
        elif water_ml <= standards["water_max"]:
            fatigue -= 3

        exercise_load = calculate_exercise_load(exercise_minutes, exercise_intensity)
        if exercise_load < standards["exercise_load_target"]:
            fatigue += min(12, (standards["exercise_load_target"] - exercise_load) / 6)
        elif exercise_load <= standards["exercise_load_upper"]:
            fatigue -= 8
        else:
            fatigue += min(10, (exercise_load - standards["exercise_load_upper"]) / 10)

        fatigue += max(0, 6 - mood_score) * 2.2
        fatigue -= max(0, mood_score - 8) * 1.5
        fatigue += BODY_STATUS_EFFECTS.get(body_status, 0)
        fatigue += SPECIAL_STATUS_EFFECTS.get(special_status, 0)

        fatigue = max(0, min(100, fatigue))
        return round(fatigue, 1)

    @staticmethod
    def calculate_legacy(sleep_hours, work_hours, game_hours, water_ml, exercise_minutes, mood_score):
        fatigue = 50

        if sleep_hours < 7:
            fatigue += (7 - sleep_hours) * 8
        else:
            fatigue -= 5

        if work_hours > 8:
            fatigue += (work_hours - 8) * 3

        if game_hours > 2:
            fatigue += (game_hours - 2) * 4

        if water_ml < 2000:
            fatigue += 5

        if exercise_minutes >= 30:
            fatigue -= 10

        fatigue += (5 - mood_score) * 2
        fatigue = max(0, min(100, fatigue))
        return round(fatigue, 2)

    @staticmethod
    def get_status(fatigue):
        if fatigue <= 30:
            return "状态良好"
        if fatigue <= 60:
            return "轻度疲劳"
        if fatigue <= 80:
            return "中度疲劳"
        return "严重疲劳"

    @staticmethod
    def build_suggestions(data, fatigue, standards):
        suggestions = []

        sleep_hours = float(data["sleep_hours"])
        work_hours = float(data["work_hours"])
        screen_hours = float(data["screen_hours"])
        water_ml = int(data["water_ml"])
        exercise_minutes = int(data["exercise_minutes"])
        exercise_intensity = data.get("exercise_intensity", "中等强度")
        exercise_load = calculate_exercise_load(exercise_minutes, exercise_intensity)
        mood_score = int(data["mood_score"])
        body_status = data.get("body_status", "无")

        if fatigue > 80:
            suggestions.append(("优先休息", "当前疲劳值较高，建议减少高强度任务，把睡眠和恢复放在第一位。"))
        if sleep_hours < standards["sleep_min"]:
            diff = round(standards["sleep_min"] - sleep_hours, 1)
            suggestions.append(("补足睡眠", f"你的年龄组建议至少睡 {standards['sleep_min']} 小时，今天少了约 {diff} 小时。"))
        if water_ml < standards["water_min"]:
            suggestions.append(("补充水分", f"按体重估算今日饮水下限约 {standards['water_min']}ml，还差约 {standards['water_min'] - water_ml}ml。"))
        if exercise_load < standards["exercise_load_target"]:
            suggestions.append(("增加轻中强度活动", f"今日等效运动量为 {exercise_load}，建议目标为 {standards['exercise_load_target']}。"))
        if exercise_load > standards["exercise_load_upper"]:
            suggestions.append(("避免运动过量", "今日运动量明显高于建议上限，注意拉伸、补水和恢复。"))
        if work_hours > standards["work_hours_max"]:
            suggestions.append(("降低连续负荷", "工作/学习时间超过个人标准，建议安排短休息，避免长时间连续消耗注意力。"))
        if screen_hours > standards["screen_hours_max"]:
            suggestions.append(("减少屏幕娱乐", "屏幕娱乐时间偏长，睡前建议减少游戏、短视频和追剧。"))
        if mood_score <= 5:
            suggestions.append(("照顾情绪", "心情评分偏低，建议安排一段没有任务压力的放松时间。"))
        if body_status != "无":
            suggestions.append(("关注身体状态", "身体不适会提高疲劳风险，今天建议以恢复为主。"))

        if not suggestions:
            suggestions.append(("状态不错", "今日数据整体接近个人标准，继续保持稳定作息和适量运动。"))
        return suggestions[:5]

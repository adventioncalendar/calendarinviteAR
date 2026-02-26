from flask import Flask, Response
from datetime import datetime, timedelta, date
import uuid
import calendar

app = Flask(__name__)

def ics_escape(text):
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace(";", "\\;")
        .replace(",", "\\,")
    )

def dtstamp_utc(dt):
    return dt.strftime("%Y%m%dT%H%M%SZ")

def yyyymmdd(d: date):
    return d.strftime("%Y%m%d")

def add_months(d: date, months: int) -> date:
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    last_day = calendar.monthrange(y, m)[1]
    day = min(d.day, last_day)
    return date(y, m, day)

@app.route("/invite.ics")
def invite():
    now = datetime.utcnow()
    base_date = now.date()  # dynamic start = download date (UTC)

    # 6 different events (each repeats every 6 months; together = monthly forever)
    events_data = [
        ("احمِ شريكك وقم بإجراء اختبار ذاتي لفيروس نقص المناعة البشرية","معرفة حالتك تساعدك على حماية نفسك وشريكك. إذا غيّرت شريكك أو لديك أي شك، قم بإجراء اختبار ذاتي لفيروس نقص المناعة البشرية اليوم."),
        ("أكد أي نتيجة تفاعلية بعد احتمال التعرض من خلال الاختبار الذاتي لفيروس نقص المناعة البشرية","بعد علاقة غير محمية أو تمزق الواقي أو مشاركة أدوات الحقن، استخدم اختبارًا ذاتيًا فورًا وقم بتأكيد أي نتيجة إيجابية في مركز صحي."),
        ("استعد لتجديد وصفة PrEP الربع سنوية من خلال الاختبار الذاتي لفيروس نقص المناعة البشرية","قبل تجديد PrEP، قم بإجراء اختبار ذاتي. الفحص كل 3 أشهر يساعدك على البقاء محميًا وبصحة جيدة."),
        ("عزز ثقتك في الاستمرار أو إعادة استخدام PrEP/PEP من خلال الاختبار الذاتي لفيروس نقص المناعة البشرية","إذا أوقفت PrEP أو تحتاج إلى PEP، ابدأ باختبار ذاتي. معرفة حالتك تساعدك على اتخاذ القرار الصحيح بسرعة وأمان."),
        ("تحكم بصحتك من خلال الكشف المبكر باستخدام الاختبار الذاتي لفيروس نقص المناعة البشرية","الكشف المبكر يعني نتائج صحية أفضل. استخدم الاختبار الذاتي بانتظام خاصة إذا كان لديك خطر مستمر."),
        ("استخدم الاختبار الذاتي كجزء من رعايتك الشخصية بعد التوقف عن PrEP","إذا أخذت استراحة من PrEP وتفكر في إعادة البدء، قم بإجراء اختبار ذاتي للتأكد من حالتك قبل استئناف الاستخدام."),
    ]

    # Alerts:
    # - Day before: midnight the day before (relative to all-day start at 00:00)
    alarm_day_before = "TRIGGER;RELATED=START:-P1D"
    # - Day of: 9am local time on the day (00:00 + 9 hours)
    alarm_day_of = "TRIGGER;RELATED=START:PT9H"

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Dynamic ICS Generator//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    for i, (title, description) in enumerate(events_data):
        start_date = add_months(base_date, i)
        end_date = start_date + timedelta(days=1)

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uuid.uuid4()}@ics-generator",
            f"DTSTAMP:{dtstamp_utc(now)}",
            f"DTSTART;VALUE=DATE:{yyyymmdd(start_date)}",
            f"DTEND;VALUE=DATE:{yyyymmdd(end_date)}",
            "RRULE:FREQ=MONTHLY;INTERVAL=6",
            f"SUMMARY:{ics_escape(title)}",
            f"DESCRIPTION:{ics_escape(description)}",

            # Alert 1: day before
            "BEGIN:VALARM",
            alarm_day_before,
            "ACTION:DISPLAY",
            "DESCRIPTION:Reminder",
            "END:VALARM",

            # Alert 2: day of (9am)
            "BEGIN:VALARM",
            alarm_day_of,
            "ACTION:DISPLAY",
            "DESCRIPTION:Reminder",
            "END:VALARM",

            "END:VEVENT",
        ])

    lines.append("END:VCALENDAR")

    ics = "\r\n".join(lines) + "\r\n"

    return Response(
        ics,
        mimetype="text/calendar",
        headers={"Content-Disposition": "attachment; filename=invite.ics"},
    )

@app.route("/")
def health():
    return "OK. Try /invite.ics"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)









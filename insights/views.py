import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from database import DatabaseManager
from importer import DataImporter
from renderer import TemplateRenderer
from templates import seed_templates, seed_templates_if_empty
from user_manager import UserManager


DB_PATH = Path(__file__).resolve().parent.parent / "fitness.db"
db = DatabaseManager(str(DB_PATH))
db.create_tables()
seed_templates_if_empty(db)
renderer = TemplateRenderer(db)
importer = DataImporter(db)
user_manager = UserManager(db)


def home(request: HttpRequest) -> HttpResponse:
    templates = db.execute(
        "SELECT template_id, template_name FROM templates ORDER BY template_id", fetchall=True
    )
    users = db.execute("SELECT user_id FROM users ORDER BY user_id LIMIT 200", fetchall=True)
    return render(
        request,
        "insights/index.html",
        {
            "templates": templates,
            "users": users,
        },
    )


@require_POST
def import_csv_view(request: HttpRequest) -> JsonResponse:
    upload = request.FILES.get("file")
    path_str = request.POST.get("path")
    try:
        if upload:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                for chunk in upload.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name
            rows = importer.import_csv(tmp_path, clear_existing=True)
            Path(tmp_path).unlink(missing_ok=True)
        else:
            csv_path = path_str or "Final_data (1).csv"
            rows = importer.import_csv(csv_path, clear_existing=True)
        return JsonResponse({"ok": True, "rows": rows})
    except Exception as exc:  # noqa: BLE001
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)


@require_POST
def seed_templates_view(request: HttpRequest) -> JsonResponse:
    try:
        seed_templates(db)
        return JsonResponse({"ok": True})
    except Exception as exc:  # noqa: BLE001
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)


@require_GET
def list_templates_view(_: HttpRequest) -> JsonResponse:
    rows = db.execute(
        "SELECT template_id, template_name FROM templates ORDER BY template_id", fetchall=True
    )
    data = [{"id": r["template_id"], "name": r["template_name"]} for r in rows or []]
    return JsonResponse({"ok": True, "templates": data})


@require_GET
def list_users_view(_: HttpRequest) -> JsonResponse:
    rows = db.execute("SELECT user_id FROM users ORDER BY user_id LIMIT 500", fetchall=True)
    return JsonResponse({"ok": True, "users": [r["user_id"] for r in rows or []]})


@require_POST
def render_template_view(request: HttpRequest) -> JsonResponse:
    try:
        template_id = int(request.POST.get("template_id", "0"))
    except ValueError:
        return JsonResponse({"ok": False, "error": "Invalid template_id"}, status=400)
    fmt = "text"
    user_val = request.POST.get("user_id")
    user_id: Optional[int] = None
    if user_val:
        try:
            user_id = int(user_val)
        except ValueError:
            user_id = None
    try:
        rendered = renderer.render(template_id, output_format=fmt, user_id=user_id)
        return JsonResponse({"ok": True, "content": rendered})
    except Exception as exc:  # noqa: BLE001
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)


@require_GET
def summary_view(_: HttpRequest) -> JsonResponse:
    data: Dict[str, Any] = {}
    try:
        # Calories by workout
        rows = db.execute(
            """
            SELECT workout_type,
                   ROUND(AVG(calories_burned), 2) AS avg_calories,
                   ROUND(AVG(session_duration), 2) AS avg_duration,
                   COUNT(*) AS sessions
            FROM workouts
            GROUP BY workout_type
            ORDER BY avg_calories DESC
            LIMIT 5
            """,
            fetchall=True,
        )
        data["calories_by_workout"] = [
            {
                "workout_type": r["workout_type"],
                "avg_calories": r["avg_calories"],
                "avg_duration": r["avg_duration"],
                "sessions": r["sessions"],
            }
            for r in rows or []
        ]

        # Top caloric deficit
        rows = db.execute(
            """
            SELECT u.user_id,
                   u.gender,
                   ROUND(u.age, 1) AS age,
                   ROUND(wa.cal_balance, 2) AS cal_balance,
                   ROUND(w.session_duration, 2) AS session_duration
            FROM workout_analysis wa
            JOIN users u ON u.user_id = wa.user_id
            JOIN workouts w ON w.user_id = u.user_id
            WHERE wa.cal_balance IS NOT NULL
            ORDER BY wa.cal_balance ASC
            LIMIT 5
            """,
            fetchall=True,
        )
        data["top_deficit"] = [
            {
                "user_id": r["user_id"],
                "gender": r["gender"],
                "age": r["age"],
                "cal_balance": r["cal_balance"],
                "session_duration": r["session_duration"],
            }
            for r in rows or []
        ]

        # Macro intake averages
        row = db.execute(
            """
            SELECT ROUND(AVG(carbs), 2) AS carbs,
                   ROUND(AVG(proteins), 2) AS proteins,
                   ROUND(AVG(fats), 2) AS fats,
                   ROUND(AVG(calories), 2) AS calories
            FROM nutrition
            """,
            fetchone=True,
        )
        if row:
            data["macro_averages"] = {
                "carbs": row["carbs"],
                "proteins": row["proteins"],
                "fats": row["fats"],
                "calories": row["calories"],
            }

        # Training efficiency
        rows = db.execute(
            """
            SELECT w.workout_type,
                   ROUND(AVG(wa.training_efficiency), 2) AS avg_efficiency,
                   ROUND(AVG(wa.muscle_focus_score), 2) AS avg_focus,
                   ROUND(AVG(wa.recovery_index), 2) AS avg_recovery
            FROM workouts w
            JOIN workout_analysis wa ON w.user_id = wa.user_id
            WHERE wa.training_efficiency IS NOT NULL
            GROUP BY w.workout_type
            ORDER BY avg_efficiency DESC
            LIMIT 5
            """,
            fetchall=True,
        )
        data["efficiency"] = [
            {
                "workout_type": r["workout_type"],
                "avg_efficiency": r["avg_efficiency"],
                "avg_focus": r["avg_focus"],
                "avg_recovery": r["avg_recovery"],
            }
            for r in rows or []
        ]

        return JsonResponse({"ok": True, "summary": data})
    except Exception as exc:  # noqa: BLE001
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)


@require_GET
def get_user_view(request: HttpRequest) -> JsonResponse:
    """获取单个用户详细信息"""
    try:
        user_id = int(request.GET.get("user_id", "0"))
    except ValueError:
        return JsonResponse({"ok": False, "error": "Invalid user_id"}, status=400)
    
    try:
        user = user_manager.get_user(user_id)
        if not user:
            return JsonResponse({"ok": False, "error": "User not found"}, status=404)
        
        # 获取用户统计信息
        stats = user_manager.get_user_statistics(user_id)
        
        return JsonResponse({
            "ok": True,
            "user": user,
            "statistics": stats or {}
        })
    except Exception as exc:  # noqa: BLE001
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)


@require_GET
def list_users_detail_view(request: HttpRequest) -> JsonResponse:
    """获取用户列表（包含详细信息）"""
    try:
        # 支持 limit/offset 或 page/page_size，默认分页
        page = int(request.GET.get("page", "1"))
        page_size = int(request.GET.get("page_size", request.GET.get("limit", "50")))
        if page < 1:
            page = 1
        if page_size <= 0:
            page_size = 50
        offset = (page - 1) * page_size
        search = request.GET.get("search", "").strip() or None
        order = (request.GET.get("order") or "desc").lower()
    except (ValueError, NameError):
        page = 1
        page_size = 50
        offset = 0
        search = None
        order = "desc"
    
    try:
        users = user_manager.list_users(
            limit=page_size,
            offset=offset,
            search=search,
            order_desc=(order != "asc"),
        )
        total = user_manager.count_users()
        return JsonResponse({
            "ok": True,
            "users": users,
            "total": total,
            "page": page,
            "page_size": page_size,
            "order": order,
        })
    except Exception as exc:  # noqa: BLE001
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)


@require_POST
def create_user_view(request: HttpRequest) -> JsonResponse:
    """创建新用户"""
    try:
        data = {}
        
        # 解析可选字段
        if request.POST.get("age"):
            data["age"] = float(request.POST.get("age"))
        if request.POST.get("gender"):
            data["gender"] = request.POST.get("gender")
        if request.POST.get("weight"):
            data["weight"] = float(request.POST.get("weight"))
        if request.POST.get("height"):
            data["height"] = float(request.POST.get("height"))
        if request.POST.get("fat_percentage"):
            data["fat_percentage"] = float(request.POST.get("fat_percentage"))
        if request.POST.get("lean_mass_kg"):
            data["lean_mass_kg"] = float(request.POST.get("lean_mass_kg"))
        if request.POST.get("workout_frequency"):
            data["workout_frequency"] = float(request.POST.get("workout_frequency"))
        if request.POST.get("water_intake"):
            data["water_intake"] = float(request.POST.get("water_intake"))
        if request.POST.get("resting_bpm"):
            data["resting_bpm"] = float(request.POST.get("resting_bpm"))
        
        user_id = user_manager.create_user(**data)
        return JsonResponse({"ok": True, "user_id": user_id})
    except ValueError as e:
        return JsonResponse({"ok": False, "error": f"Invalid input: {e}"}, status=400)
    except Exception as exc:  # noqa: BLE001
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)


@require_POST
def update_user_view(request: HttpRequest) -> JsonResponse:
    """更新用户信息"""
    try:
        user_id = int(request.POST.get("user_id", "0"))
    except ValueError:
        return JsonResponse({"ok": False, "error": "Invalid user_id"}, status=400)
    
    try:
        data = {}
        
        # 解析可选字段
        if request.POST.get("age"):
            data["age"] = float(request.POST.get("age"))
        if request.POST.get("gender"):
            data["gender"] = request.POST.get("gender")
        if request.POST.get("weight"):
            data["weight"] = float(request.POST.get("weight"))
        if request.POST.get("height"):
            data["height"] = float(request.POST.get("height"))
        if request.POST.get("fat_percentage"):
            data["fat_percentage"] = float(request.POST.get("fat_percentage"))
        if request.POST.get("lean_mass_kg"):
            data["lean_mass_kg"] = float(request.POST.get("lean_mass_kg"))
        if request.POST.get("workout_frequency"):
            data["workout_frequency"] = float(request.POST.get("workout_frequency"))
        if request.POST.get("water_intake"):
            data["water_intake"] = float(request.POST.get("water_intake"))
        if request.POST.get("resting_bpm"):
            data["resting_bpm"] = float(request.POST.get("resting_bpm"))
        
        success = user_manager.update_user(user_id, **data)
        if not success:
            return JsonResponse({"ok": False, "error": "User not found or update failed"}, status=404)
        
        return JsonResponse({"ok": True, "user_id": user_id})
    except ValueError as e:
        return JsonResponse({"ok": False, "error": f"Invalid input: {e}"}, status=400)
    except Exception as exc:  # noqa: BLE001
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)


@require_POST
def delete_user_view(request: HttpRequest) -> JsonResponse:
    """删除用户"""
    try:
        user_id = int(request.POST.get("user_id", "0"))
        cascade = request.POST.get("cascade", "false").lower() == "true"
    except ValueError:
        return JsonResponse({"ok": False, "error": "Invalid user_id"}, status=400)
    
    try:
        existing_user = user_manager.get_user(user_id)
        if not existing_user:
            return JsonResponse({"ok": False, "error": "用户不存在"}, status=404)

        success = user_manager.delete_user(user_id, cascade=cascade)
        if success and not user_manager.get_user(user_id):
            return JsonResponse({"ok": True, "user_id": user_id})

        return JsonResponse({"ok": False, "error": "删除失败，用户仍存在"}, status=500)
    except Exception as exc:  # noqa: BLE001
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)

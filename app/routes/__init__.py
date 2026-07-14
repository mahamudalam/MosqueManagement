from .auth import auth_bp
from .dashboard import dashboard_bp
from .members import members_bp
from .imam import imam_bp
from .friday import friday_bp
from .general_contribution import general_contribution_bp
from .salary import salary_bp
from .reports import reports_bp
from .prayer import prayer_bp
from .contact import contact_bp
from .expense import expense_bp






def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(imam_bp)
    app.register_blueprint(friday_bp)
    app.register_blueprint(general_contribution_bp)
    app.register_blueprint(salary_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(prayer_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(expense_bp)

    return app


__all__ = ["register_routes"]

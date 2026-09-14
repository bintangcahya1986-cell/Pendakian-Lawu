"""
User blueprint — participant-facing routes.
Prefix: /user
"""
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, session)
from ..database import db
from ..models import User, Savings, ClimbingInfo
from ..decorators import user_required

user_bp = Blueprint('user', __name__)


# ══════════════════════════════════════════════════════════════
# Dashboard  (task 6)
# ══════════════════════════════════════════════════════════════

@user_bp.route('/dashboard')
@user_required
def dashboard():
    user = User.query.get_or_404(session['user_id'])
    active_event = ClimbingInfo.query.filter_by(is_active=True).first()
    # Latest 5 savings for the quick-preview table
    recent_savings = (Savings.query
                      .filter_by(user_id=user.id)
                      .order_by(Savings.submitted_at.desc())
                      .limit(5).all())
    return render_template('user/dashboard.html',
                           user=user,
                           active_event=active_event,
                           recent_savings=recent_savings)


# ══════════════════════════════════════════════════════════════
# Record savings  (task 8)
# ══════════════════════════════════════════════════════════════

@user_bp.route('/savings/add', methods=['GET', 'POST'])
@user_required
def add_saving():
    user = User.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        amount_str  = request.form.get('amount', '').strip()
        description = request.form.get('description', '').strip()

        errors = []
        if not amount_str:
            errors.append('Jumlah tabungan wajib diisi.')
        else:
            try:
                amount = float(amount_str.replace(',', '').replace('.', ''))
                if amount <= 0:
                    errors.append('Jumlah tabungan harus lebih dari 0.')
            except ValueError:
                errors.append('Jumlah tabungan harus berupa angka.')
                amount = 0

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('user/add_saving.html', user=user, form=request.form)

        saving = Savings(
            user_id=user.id,
            amount=amount,
            description=description or None,
            status='pending',
        )
        db.session.add(saving)
        db.session.commit()
        flash('Tabungan berhasil dicatat dan menunggu verifikasi Admin.', 'success')
        return redirect(url_for('user.dashboard'))

    return render_template('user/add_saving.html', user=user, form={})


# ══════════════════════════════════════════════════════════════
# Savings History  (task 10)
# ══════════════════════════════════════════════════════════════

@user_bp.route('/savings/history')
@user_required
def savings_history():
    user = User.query.get_or_404(session['user_id'])
    status = request.args.get('status', '')
    query  = Savings.query.filter_by(user_id=user.id).order_by(Savings.submitted_at.desc())
    if status in ('pending', 'verified', 'rejected'):
        query = query.filter_by(status=status)
    savings_list = query.all()
    return render_template('user/savings_history.html',
                           user=user,
                           savings_list=savings_list,
                           selected_status=status)


# ══════════════════════════════════════════════════════════════
# Climbing Information  (task 11)
# ══════════════════════════════════════════════════════════════

@user_bp.route('/climbing')
@user_required
def climbing_info():
    active_event = ClimbingInfo.query.filter_by(is_active=True).first()
    return render_template('user/climbing_info.html', event=active_event)


@user_bp.route('/climbing/route')
@user_required
def climbing_route():
    active_event = ClimbingInfo.query.filter_by(is_active=True).first()
    return render_template('user/climbing_route.html', event=active_event)

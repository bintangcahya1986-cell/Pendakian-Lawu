"""
Admin blueprint — all admin-only routes.
Prefix: /admin
"""
from datetime import datetime
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, session, abort)
from werkzeug.security import generate_password_hash
from ..database import db
from ..models import User, Savings, ClimbingInfo, RouteItem
from ..decorators import admin_required

admin_bp = Blueprint('admin', __name__)


# ── Helpers ────────────────────────────────────────────────

def _get_stats():
    participants = User.query.filter_by(role='user').all()
    pending_count = Savings.query.filter_by(status='pending').count()
    total_verified = db.session.query(db.func.sum(Savings.amount)).filter_by(status='verified').scalar() or 0
    return participants, pending_count, total_verified


# ══════════════════════════════════════════════════════════════
# Dashboard
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    participants, pending_count, total_verified = _get_stats()
    # Recent 5 pending savings
    pending_savings = (Savings.query
                       .filter_by(status='pending')
                       .order_by(Savings.submitted_at.desc())
                       .limit(5).all())
    active_event = ClimbingInfo.query.filter_by(is_active=True).first()
    return render_template('admin/dashboard.html',
                           participants=participants,
                           pending_count=pending_count,
                           total_verified=total_verified,
                           pending_savings=pending_savings,
                           active_event=active_event)


# ══════════════════════════════════════════════════════════════
# Participant Management  (tasks 7)
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/participants')
@admin_required
def participants():
    users = User.query.filter_by(role='user').order_by(User.full_name).all()
    return render_template('admin/participants.html', users=users)


@admin_bp.route('/participants/add', methods=['GET', 'POST'])
@admin_required
def add_participant():
    if request.method == 'POST':
        full_name    = request.form.get('full_name', '').strip()
        username     = request.form.get('username', '').strip()
        password     = request.form.get('password', '')
        target       = request.form.get('target_amount', '').strip()
        phone        = request.form.get('phone_number', '').strip()
        notes        = request.form.get('notes', '').strip()

        errors = []
        if not full_name: errors.append('Nama lengkap wajib diisi.')
        if not username:  errors.append('Username wajib diisi.')
        if not password:  errors.append('Password wajib diisi.')
        if User.query.filter_by(username=username).first():
            errors.append(f'Username "{username}" sudah digunakan.')

        try:
            target_val = float(target) if target else None
            if target_val is not None and target_val < 0:
                errors.append('Target tabungan tidak boleh negatif.')
        except ValueError:
            errors.append('Target tabungan harus berupa angka.')
            target_val = None

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('admin/participant_form.html',
                                   action='add', form=request.form)

        user = User(
            full_name=full_name,
            username=username,
            password_hash=generate_password_hash(password),
            role='user',
            is_active=True,
            target_amount=target_val,
            phone_number=phone or None,
            notes=notes or None,
        )
        db.session.add(user)
        db.session.commit()
        flash(f'Peserta "{full_name}" berhasil ditambahkan.', 'success')
        return redirect(url_for('admin.participants'))

    return render_template('admin/participant_form.html', action='add', form={})


@admin_bp.route('/participants/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_participant(user_id):
    user = User.query.filter_by(id=user_id, role='user').first_or_404()

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username  = request.form.get('username', '').strip()
        password  = request.form.get('password', '').strip()
        target    = request.form.get('target_amount', '').strip()
        phone     = request.form.get('phone_number', '').strip()
        notes     = request.form.get('notes', '').strip()
        is_active = request.form.get('is_active') == '1'

        errors = []
        if not full_name: errors.append('Nama lengkap wajib diisi.')
        if not username:  errors.append('Username wajib diisi.')

        # Check username uniqueness (excluding self)
        existing = User.query.filter_by(username=username).first()
        if existing and existing.id != user_id:
            errors.append(f'Username "{username}" sudah digunakan.')

        try:
            target_val = float(target) if target else None
        except ValueError:
            errors.append('Target tabungan harus berupa angka.')
            target_val = user.target_amount

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('admin/participant_form.html',
                                   action='edit', user=user, form=request.form)

        user.full_name    = full_name
        user.username     = username
        user.target_amount = target_val
        user.phone_number = phone or None
        user.notes        = notes or None
        user.is_active    = is_active
        user.updated_at   = datetime.utcnow()

        if password:
            user.password_hash = generate_password_hash(password)

        db.session.commit()
        flash(f'Data peserta "{full_name}" berhasil diperbarui.', 'success')
        return redirect(url_for('admin.participants'))

    return render_template('admin/participant_form.html',
                           action='edit', user=user, form=user.__dict__)


@admin_bp.route('/participants/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_participant(user_id):
    user = User.query.filter_by(id=user_id, role='user').first_or_404()
    user.is_active = not user.is_active
    db.session.commit()
    status = 'diaktifkan' if user.is_active else 'dinonaktifkan'
    flash(f'Akun "{user.full_name}" berhasil {status}.', 'success')
    return redirect(url_for('admin.participants'))


# ══════════════════════════════════════════════════════════════
# Savings Verification  (task 9)
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/verifications')
@admin_required
def verifications():
    status_filter = request.args.get('status', 'pending')
    query = Savings.query.order_by(Savings.submitted_at.desc())
    if status_filter in ('pending', 'verified', 'rejected'):
        query = query.filter_by(status=status_filter)
    savings_list = query.all()
    return render_template('admin/verifications.html',
                           savings_list=savings_list,
                           status_filter=status_filter)


@admin_bp.route('/verifications/<int:saving_id>/verify', methods=['POST'])
@admin_required
def verify_saving(saving_id):
    saving = Savings.query.get_or_404(saving_id)
    if saving.status != 'pending':
        flash('Tabungan ini sudah diproses sebelumnya.', 'warning')
        return redirect(url_for('admin.verifications'))

    action = request.form.get('action')
    rejection_note = request.form.get('rejection_note', '').strip()

    if action == 'approve':
        saving.status      = 'verified'
        saving.verified_by = session['user_id']
        saving.verified_at = datetime.utcnow()
        saving.rejection_note = None
        db.session.commit()
        flash(f'Tabungan Rp {saving.amount:,.0f} dari {saving.participant.full_name} disetujui.', 'success')

    elif action == 'reject':
        saving.status         = 'rejected'
        saving.verified_by    = session['user_id']
        saving.verified_at    = datetime.utcnow()
        saving.rejection_note = rejection_note or 'Ditolak oleh Admin.'
        db.session.commit()
        flash(f'Tabungan dari {saving.participant.full_name} ditolak.', 'warning')

    else:
        flash('Aksi tidak dikenali.', 'error')

    return redirect(url_for('admin.verifications'))


# ══════════════════════════════════════════════════════════════
# Savings History — admin view  (task 10)
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/savings')
@admin_required
def savings_history():
    user_id = request.args.get('user_id', type=int)
    status  = request.args.get('status', '')
    query   = Savings.query.order_by(Savings.submitted_at.desc())
    if user_id:
        query = query.filter_by(user_id=user_id)
    if status in ('pending', 'verified', 'rejected'):
        query = query.filter_by(status=status)
    savings_list = query.all()
    participants = User.query.filter_by(role='user').order_by(User.full_name).all()
    return render_template('admin/savings_history.html',
                           savings_list=savings_list,
                           participants=participants,
                           selected_user=user_id,
                           selected_status=status)


# ══════════════════════════════════════════════════════════════
# Climbing Information  (task 11)
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/climbing')
@admin_required
def climbing_list():
    events = ClimbingInfo.query.order_by(ClimbingInfo.created_at.desc()).all()
    return render_template('admin/climbing_list.html', events=events)


@admin_bp.route('/climbing/add', methods=['GET', 'POST'])
@admin_required
def add_climbing():
    if request.method == 'POST':
        name      = request.form.get('mountain_name', '').strip()
        date      = request.form.get('climb_date', '').strip()
        meeting   = request.form.get('meeting_point', '').strip()
        desc      = request.form.get('description', '').strip()
        equipment = request.form.get('equipment_notes', '').strip()
        important = request.form.get('important_notes', '').strip()
        make_active = request.form.get('is_active') == '1'

        if not name:
            flash('Nama gunung wajib diisi.', 'error')
            return render_template('admin/climbing_form.html', action='add', form=request.form)

        # Deactivate others if this will be active
        if make_active:
            ClimbingInfo.query.update({'is_active': False})

        event = ClimbingInfo(
            mountain_name=name,
            climb_date=date or None,
            meeting_point=meeting or None,
            description=desc or None,
            equipment_notes=equipment or None,
            important_notes=important or None,
            is_active=make_active,
        )
        db.session.add(event)
        db.session.commit()
        flash(f'Informasi pendakian "{name}" berhasil ditambahkan.', 'success')
        return redirect(url_for('admin.climbing_list'))

    return render_template('admin/climbing_form.html', action='add', form={})


@admin_bp.route('/climbing/<int:event_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_climbing(event_id):
    event = ClimbingInfo.query.get_or_404(event_id)

    if request.method == 'POST':
        event.mountain_name   = request.form.get('mountain_name', '').strip()
        event.climb_date      = request.form.get('climb_date', '').strip() or None
        event.meeting_point   = request.form.get('meeting_point', '').strip() or None
        event.description     = request.form.get('description', '').strip() or None
        event.equipment_notes = request.form.get('equipment_notes', '').strip() or None
        event.important_notes = request.form.get('important_notes', '').strip() or None
        make_active = request.form.get('is_active') == '1'

        if make_active and not event.is_active:
            ClimbingInfo.query.filter(ClimbingInfo.id != event_id).update({'is_active': False})

        event.is_active  = make_active
        event.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Informasi pendakian berhasil diperbarui.', 'success')
        return redirect(url_for('admin.climbing_list'))

    return render_template('admin/climbing_form.html', action='edit', event=event, form=event.__dict__)


@admin_bp.route('/climbing/<int:event_id>/delete', methods=['POST'])
@admin_required
def delete_climbing(event_id):
    event = ClimbingInfo.query.get_or_404(event_id)
    name = event.mountain_name
    db.session.delete(event)
    db.session.commit()
    flash(f'Informasi pendakian "{name}" berhasil dihapus.', 'success')
    return redirect(url_for('admin.climbing_list'))


# ══════════════════════════════════════════════════════════════
# Route / Itinerary  (task 12)
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/climbing/<int:event_id>/routes')
@admin_required
def route_list(event_id):
    event = ClimbingInfo.query.get_or_404(event_id)
    return render_template('admin/route_list.html', event=event)


@admin_bp.route('/climbing/<int:event_id>/routes/add', methods=['GET', 'POST'])
@admin_required
def add_route_item(event_id):
    event = ClimbingInfo.query.get_or_404(event_id)

    if request.method == 'POST':
        title      = request.form.get('title', '').strip()
        item_type  = request.form.get('item_type', 'checkpoint')
        content    = request.form.get('content', '').strip()
        elevation  = request.form.get('elevation', '').strip()
        duration   = request.form.get('duration', '').strip()

        try:
            order_index = int(request.form.get('order_index', 0))
        except ValueError:
            order_index = 0

        if not title:
            flash('Judul wajib diisi.', 'error')
            return render_template('admin/route_form.html',
                                   action='add', event=event, form=request.form)

        item = RouteItem(
            climbing_info_id=event_id,
            title=title,
            item_type=item_type,
            content=content or None,
            elevation=elevation or None,
            duration=duration or None,
            order_index=order_index,
        )
        db.session.add(item)
        db.session.commit()
        flash(f'Item rute "{title}" berhasil ditambahkan.', 'success')
        return redirect(url_for('admin.route_list', event_id=event_id))

    # Auto next order
    max_order = db.session.query(db.func.max(RouteItem.order_index)).filter_by(
        climbing_info_id=event_id).scalar() or -1
    return render_template('admin/route_form.html',
                           action='add', event=event,
                           form={'order_index': max_order + 1})


@admin_bp.route('/climbing/<int:event_id>/routes/<int:item_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_route_item(event_id, item_id):
    event = ClimbingInfo.query.get_or_404(event_id)
    item  = RouteItem.query.filter_by(id=item_id, climbing_info_id=event_id).first_or_404()

    if request.method == 'POST':
        item.title      = request.form.get('title', '').strip()
        item.item_type  = request.form.get('item_type', 'checkpoint')
        item.content    = request.form.get('content', '').strip() or None
        item.elevation  = request.form.get('elevation', '').strip() or None
        item.duration   = request.form.get('duration', '').strip() or None
        try:
            item.order_index = int(request.form.get('order_index', item.order_index))
        except ValueError:
            pass

        db.session.commit()
        flash(f'Item rute "{item.title}" berhasil diperbarui.', 'success')
        return redirect(url_for('admin.route_list', event_id=event_id))

    return render_template('admin/route_form.html',
                           action='edit', event=event, item=item, form=item.__dict__)


@admin_bp.route('/climbing/<int:event_id>/routes/<int:item_id>/delete', methods=['POST'])
@admin_required
def delete_route_item(event_id, item_id):
    item = RouteItem.query.filter_by(id=item_id, climbing_info_id=event_id).first_or_404()
    title = item.title
    db.session.delete(item)
    db.session.commit()
    flash(f'Item "{title}" berhasil dihapus.', 'success')
    return redirect(url_for('admin.route_list', event_id=event_id))

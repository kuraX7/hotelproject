/**
 * Al Andalus Hotel — Availability Calendar Widget
 * Premium visual calendar with date range selection
 */

class AvailabilityCalendar {
  constructor(options) {
    this.containerId   = options.containerId;
    this.roomId        = options.roomId;
    this.pricePerNight = options.pricePerNight || 0;
    this.onDateSelect  = options.onDateSelect || (() => {});
    this.calendarUrl   = options.calendarUrl;

    this.today       = new Date();
    this.today.setHours(0, 0, 0, 0);
    this.viewMonth   = new Date(this.today.getFullYear(), this.today.getMonth(), 1);

    this.checkIn     = null;
    this.checkOut    = null;
    this.hoveredDate = null;
    this.bookedDates = new Set();
    this.selecting   = 'checkin'; // 'checkin' or 'checkout'

    this.monthNames = [
      'Janvier','Février','Mars','Avril','Mai','Juin',
      'Juillet','Août','Septembre','Octobre','Novembre','Décembre'
    ];
    this.dayNames = ['Lun','Mar','Mer','Jeu','Ven','Sam','Dim'];

    this._loadData();
  }

  _loadData() {
    const container = document.getElementById(this.containerId);
    if (!container) return;
    container.innerHTML = `
      <div style="display:flex;align-items:center;justify-content:center;padding:40px;color:#9CA3AF">
        <div style="text-align:center">
          <div class="calendar-spinner"></div>
          <div style="margin-top:12px;font-size:.83rem">Chargement du calendrier...</div>
        </div>
      </div>`;

    fetch(this.calendarUrl)
      .then(r => r.json())
      .then(data => {
        this.bookedDates = new Set(data.booked_dates || []);
        this.pricePerNight = data.price || this.pricePerNight;
        this._render();
      })
      .catch(() => {
        container.innerHTML = '<div style="padding:20px;text-align:center;color:#EF4444">Impossible de charger le calendrier.</div>';
      });
  }

  _isoDate(d) {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;
  }

  _isBooked(d) {
    return this.bookedDates.has(this._isoDate(d));
  }

  _isPast(d) {
    return d < this.today;
  }

  _isDisabled(d) {
    return this._isPast(d) || this._isBooked(d);
  }

  _isInRange(d) {
    if (!this.checkIn) return false;
    const end = this.checkOut || this.hoveredDate;
    if (!end) return false;
    const from = this.checkIn < end ? this.checkIn : end;
    const to   = this.checkIn < end ? end : this.checkIn;
    return d > from && d < to;
  }

  _isSelected(d) {
    if (this.checkIn && this._isoDate(d) === this._isoDate(this.checkIn)) return 'checkin';
    if (this.checkOut && this._isoDate(d) === this._isoDate(this.checkOut)) return 'checkout';
    return false;
  }

  _hasBookedInRange(from, to) {
    const start = new Date(from);
    const end   = new Date(to);
    const cur   = new Date(start);
    cur.setDate(cur.getDate() + 1);
    while (cur < end) {
      if (this._isBooked(cur)) return true;
      cur.setDate(cur.getDate() + 1);
    }
    return false;
  }

  _renderMonth(year, month) {
    const firstDay = new Date(year, month, 1);
    const lastDay  = new Date(year, month + 1, 0);

    // Monday-first: (getDay() + 6) % 7
    let startDow = (firstDay.getDay() + 6) % 7;

    let html = `
      <div class="cal-month">
        <div class="cal-month-header">
          <span class="cal-month-name">${this.monthNames[month]} ${year}</span>
        </div>
        <div class="cal-grid">`;

    // Day headers
    this.dayNames.forEach(d => {
      html += `<div class="cal-day-header">${d}</div>`;
    });

    // Empty cells before first day
    for (let i = 0; i < startDow; i++) {
      html += `<div class="cal-day cal-empty"></div>`;
    }

    // Days
    for (let day = 1; day <= lastDay.getDate(); day++) {
      const d = new Date(year, month, day);
      const iso = this._isoDate(d);
      const isToday    = iso === this._isoDate(this.today);
      const disabled   = this._isDisabled(d);
      const booked     = this._isBooked(d);
      const past       = this._isPast(d);
      const selected   = this._isSelected(d);
      const inRange    = this._isInRange(d);
      const isCheckIn  = selected === 'checkin';
      const isCheckOut = selected === 'checkout';

      let cls = 'cal-day';
      if (past)       cls += ' cal-past';
      else if (booked) cls += ' cal-booked';
      else             cls += ' cal-available';
      if (isToday)    cls += ' cal-today';
      if (inRange)    cls += ' cal-in-range';
      if (isCheckIn)  cls += ' cal-selected cal-checkin';
      if (isCheckOut) cls += ' cal-selected cal-checkout';
      if (!disabled)  cls += ' cal-clickable';

      const tooltip = booked ? 'Réservé' : past ? 'Date passée' : '';

      html += `<div class="${cls}" data-date="${iso}" title="${tooltip}">${day}</div>`;
    }

    html += `</div></div>`;
    return html;
  }

  _render() {
    const container = document.getElementById(this.containerId);
    if (!container) return;

    const y = this.viewMonth.getFullYear();
    const m = this.viewMonth.getMonth();

    // Next month
    const nextDate = new Date(y, m + 1, 1);
    const ny = nextDate.getFullYear();
    const nm = nextDate.getMonth();

    // Summary bar
    let summaryHtml = '';
    if (this.checkIn && this.checkOut) {
      const nights = Math.round((this.checkOut - this.checkIn) / 86400000);
      const total  = nights * this.pricePerNight;
      summaryHtml = `
        <div class="cal-summary">
          <div class="cal-summary-item">
            <div class="cal-summary-label">Arrivée</div>
            <div class="cal-summary-value">${this._formatDate(this.checkIn)}</div>
          </div>
          <div class="cal-summary-arrow"><i class="fas fa-arrow-right"></i></div>
          <div class="cal-summary-item">
            <div class="cal-summary-label">Départ</div>
            <div class="cal-summary-value">${this._formatDate(this.checkOut)}</div>
          </div>
          <div class="cal-summary-nights">
            <div class="cal-summary-label">Durée</div>
            <div class="cal-summary-value">${nights} nuit${nights > 1 ? 's' : ''}</div>
          </div>
          <div class="cal-summary-total">
            <div class="cal-summary-label">Total</div>
            <div class="cal-summary-price">${total.toLocaleString('fr-MA')} MAD</div>
          </div>
        </div>`;
    } else if (this.checkIn) {
      summaryHtml = `
        <div class="cal-summary cal-summary-partial">
          <div class="cal-summary-hint">
            <i class="fas fa-hand-pointer me-2" style="color:#C9A96E"></i>
            Arrivée : <strong>${this._formatDate(this.checkIn)}</strong> — Sélectionnez maintenant la date de départ
          </div>
        </div>`;
    } else {
      summaryHtml = `
        <div class="cal-summary cal-summary-empty">
          <i class="fas fa-calendar-alt me-2" style="color:#C9A96E"></i>
          Cliquez sur une date pour sélectionner votre arrivée
        </div>`;
    }

    const prevDisabled = this.viewMonth <= new Date(this.today.getFullYear(), this.today.getMonth(), 1);

    container.innerHTML = `
      <div class="cal-wrapper">
        <!-- Header nav -->
        <div class="cal-nav">
          <button class="cal-nav-btn" id="cal-prev" ${prevDisabled ? 'disabled' : ''}>
            <i class="fas fa-chevron-left"></i>
          </button>
          <div class="cal-nav-title">Sélectionnez vos dates de séjour</div>
          <button class="cal-nav-btn" id="cal-next">
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>

        <!-- Two months -->
        <div class="cal-months-row">
          ${this._renderMonth(y, m)}
          ${this._renderMonth(ny, nm)}
        </div>

        <!-- Legend -->
        <div class="cal-legend">
          <div class="cal-legend-item"><div class="cal-legend-dot cal-legend-available"></div>Disponible</div>
          <div class="cal-legend-item"><div class="cal-legend-dot cal-legend-selected"></div>Sélectionné</div>
          <div class="cal-legend-item"><div class="cal-legend-dot cal-legend-range"></div>Séjour</div>
          <div class="cal-legend-item"><div class="cal-legend-dot cal-legend-booked"></div>Réservé</div>
        </div>

        <!-- Summary / action bar -->
        ${summaryHtml}

        <!-- Book button -->
        ${this.checkIn && this.checkOut ? `
        <div style="padding:0 16px 16px">
          <button class="cal-book-btn" id="cal-book-btn">
            <i class="fas fa-calendar-check me-2"></i>Réserver ces dates
          </button>
        </div>` : ''}

        <!-- Reset -->
        ${this.checkIn ? `
        <div style="padding:0 16px 12px;text-align:center">
          <button class="cal-reset-btn" id="cal-reset">
            <i class="fas fa-times me-1"></i>Réinitialiser les dates
          </button>
        </div>` : ''}
      </div>`;

    this._attachEvents(container);
  }

  _formatDate(d) {
    const days = ['Dim','Lun','Mar','Mer','Jeu','Ven','Sam'];
    const months = ['jan','fév','mar','avr','mai','juin','jul','août','sep','oct','nov','déc'];
    return `${days[d.getDay()]} ${d.getDate()} ${months[d.getMonth()]} ${d.getFullYear()}`;
  }

  _attachEvents(container) {
    // Prev month
    const prevBtn = container.querySelector('#cal-prev');
    if (prevBtn) prevBtn.onclick = () => {
      this.viewMonth = new Date(this.viewMonth.getFullYear(), this.viewMonth.getMonth() - 1, 1);
      this._render();
    };

    // Next month (max 12 months ahead)
    const nextBtn = container.querySelector('#cal-next');
    if (nextBtn) nextBtn.onclick = () => {
      const maxMonth = new Date(this.today.getFullYear(), this.today.getMonth() + 11, 1);
      if (this.viewMonth < maxMonth) {
        this.viewMonth = new Date(this.viewMonth.getFullYear(), this.viewMonth.getMonth() + 1, 1);
        this._render();
      }
    };

    // Reset
    const resetBtn = container.querySelector('#cal-reset');
    if (resetBtn) resetBtn.onclick = () => {
      this.checkIn = this.checkOut = null;
      this.selecting = 'checkin';
      this._render();
      this.onDateSelect(null, null);
    };

    // Book button
    const bookBtn = container.querySelector('#cal-book-btn');
    if (bookBtn) bookBtn.onclick = () => {
      if (this.checkIn && this.checkOut) {
        this.onDateSelect(this._isoDate(this.checkIn), this._isoDate(this.checkOut));
      }
    };

    // Day clicks
    container.querySelectorAll('.cal-day.cal-clickable').forEach(dayEl => {
      dayEl.onclick = () => this._handleDayClick(dayEl.dataset.date);
      dayEl.onmouseenter = () => {
        if (this.checkIn && !this.checkOut) {
          this.hoveredDate = new Date(dayEl.dataset.date + 'T00:00:00');
          this._render();
        }
      };
    });
  }

  _handleDayClick(isoDate) {
    const clicked = new Date(isoDate + 'T00:00:00');

    if (this.selecting === 'checkin' || (this.checkIn && this.checkOut)) {
      // Start fresh selection
      this.checkIn   = clicked;
      this.checkOut  = null;
      this.hoveredDate = null;
      this.selecting = 'checkout';
    } else {
      // Selecting checkout
      if (clicked <= this.checkIn) {
        // Clicked before check-in: restart
        this.checkIn   = clicked;
        this.checkOut  = null;
        this.selecting = 'checkout';
      } else if (this._hasBookedInRange(this.checkIn, clicked)) {
        // Range crosses booked dates
        this.checkIn   = clicked;
        this.checkOut  = null;
        this.selecting = 'checkout';
      } else {
        this.checkOut  = clicked;
        this.hoveredDate = null;
        this.selecting = 'checkin';
        this.onDateSelect(this._isoDate(this.checkIn), this._isoDate(this.checkOut));
      }
    }
    this._render();
  }
}

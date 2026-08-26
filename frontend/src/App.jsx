import {
  AlertCircle,
  Armchair,
  ArrowLeftRight,
  BadgeCheck,
  Bus,
  CalendarDays,
  CheckCircle2,
  ChevronRight,
  Clock3,
  CreditCard,
  Languages,
  Minus,
  Plus,
  ReceiptText,
  RefreshCw,
  Search,
  ShieldCheck,
  Sparkles,
  Ticket,
  Trash2,
  UserRound,
  XCircle,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import MasarProduct from "./MasarProduct";
import EasternMasar from "./EasternMasar";

const API_CANDIDATES = ["http://127.0.0.1:8000", "http://127.0.0.1:8022"];
const STORAGE_KEY = "masar-reservations-v1";

const cities = [
  "Riyadh",
  "Jeddah",
  "Dammam",
  "Makkah",
  "Madinah",
  "Taif",
  "Abha",
  "Tabuk",
  "AlUla",
];

const fleet = [
  {
    id: "MSR-101",
    from: "Riyadh",
    to: "Jeddah",
    depart: "07:30",
    arrive: "18:10",
    duration: "10h 40m",
    basePrice: 165,
    seats: 40,
    booked: [1, 2, 6, 8, 15, 16, 23, 27, 31, 32, 37],
    rating: 4.8,
    tags: ["Express", "Wi-Fi", "Women seats"],
  },
  {
    id: "MSR-124",
    from: "Riyadh",
    to: "Jeddah",
    depart: "22:15",
    arrive: "08:50",
    duration: "10h 35m",
    basePrice: 148,
    seats: 44,
    booked: [4, 5, 11, 12, 19, 20, 28, 35, 41, 42, 43],
    rating: 4.6,
    tags: ["Night", "Sleeper seats", "Quiet"],
  },
  {
    id: "MSR-218",
    from: "Jeddah",
    to: "Makkah",
    depart: "09:00",
    arrive: "10:25",
    duration: "1h 25m",
    basePrice: 35,
    seats: 36,
    booked: [3, 7, 12, 13, 14, 21, 29, 30],
    rating: 4.7,
    tags: ["Shuttle", "Accessible", "Frequent"],
  },
  {
    id: "MSR-330",
    from: "Dammam",
    to: "Riyadh",
    depart: "06:45",
    arrive: "11:30",
    duration: "4h 45m",
    basePrice: 88,
    seats: 40,
    booked: [9, 10, 17, 18, 25, 33, 34, 39, 40],
    rating: 4.5,
    tags: ["Business", "Power outlets", "Fast"],
  },
  {
    id: "MSR-412",
    from: "Madinah",
    to: "AlUla",
    depart: "13:20",
    arrive: "18:05",
    duration: "4h 45m",
    basePrice: 96,
    seats: 32,
    booked: [2, 8, 16, 17, 22, 23, 24, 31],
    rating: 4.9,
    tags: ["Scenic", "Low stops", "Wi-Fi"],
  },
  {
    id: "MSR-516",
    from: "Abha",
    to: "Taif",
    depart: "15:10",
    arrive: "22:35",
    duration: "7h 25m",
    basePrice: 117,
    seats: 36,
    booked: [1, 5, 6, 10, 18, 19, 20, 26, 27, 35],
    rating: 4.4,
    tags: ["Mountain", "Meal stop", "Accessible"],
  },
  {
    id: "MSR-601",
    from: "Tabuk",
    to: "Madinah",
    depart: "08:40",
    arrive: "15:55",
    duration: "7h 15m",
    basePrice: 104,
    seats: 40,
    booked: [3, 4, 13, 14, 22, 30, 38],
    rating: 4.6,
    tags: ["Direct", "USB", "Wi-Fi"],
  },
];

const emptyPassenger = { name: "", nationalId: "", type: "adult" };

function tomorrow() {
  const value = new Date();
  value.setDate(value.getDate() + 1);
  return value.toISOString().slice(0, 10);
}

function addDays(date, days) {
  const value = new Date(`${date}T12:00:00`);
  value.setDate(value.getDate() + days);
  return value.toISOString().slice(0, 10);
}

function formatMoney(amount) {
  return new Intl.NumberFormat("en-SA", { style: "currency", currency: "SAR", maximumFractionDigits: 0 }).format(amount);
}

function safeReadReservations() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
  } catch {
    return [];
  }
}

function maskCard(number) {
  const digits = number.replace(/\D/g, "");
  return digits.length >= 4 ? `**** ${digits.slice(-4)}` : "Cash counter";
}

function luhn(value) {
  const digits = value.replace(/\D/g, "");
  if (digits.length < 13 || digits.length > 19) return false;
  let sum = 0;
  let double = false;
  for (let index = digits.length - 1; index >= 0; index -= 1) {
    let digit = Number(digits[index]);
    if (double) {
      digit *= 2;
      if (digit > 9) digit -= 9;
    }
    sum += digit;
    double = !double;
  }
  return sum % 10 === 0;
}

function makeTripInstances(query, reservations) {
  return fleet.map((trip, index) => {
    const reservedSeats = reservations
      .filter((reservation) => reservation.status === "confirmed" && reservation.tripId === trip.id && reservation.date === query.departDate)
      .flatMap((reservation) => reservation.seats);
    const booked = [...new Set([...trip.booked, ...reservedSeats])];
    const demand = query.passengers >= 5 ? 0.98 : booked.length / trip.seats;
    const surge = query.tripType === "round" ? 0.94 : 1;
    const datePremium = new Date(`${query.departDate}T12:00:00`).getDay() % 5 === 4 ? 1.12 : 1;
    return {
      ...trip,
      delayRisk: index % 3 === 0 ? "Low" : index % 3 === 1 ? "Medium" : "Low",
      booked,
      remaining: trip.seats - booked.length,
      price: Math.round(trip.basePrice * surge * datePremium),
      demand,
    };
  });
}

export default function App() {
  return <EasternMasar />;

  const [language, setLanguage] = useState("en");
  const [query, setQuery] = useState({
    tripType: "one-way",
    from: "Riyadh",
    to: "Jeddah",
    departDate: tomorrow(),
    returnDate: addDays(tomorrow(), 3),
    passengers: 1,
    cabin: "standard",
    accessible: false,
  });
  const [reservations, setReservations] = useState(safeReadReservations);
  const [selectedTripId, setSelectedTripId] = useState("MSR-101");
  const [selectedSeats, setSelectedSeats] = useState([]);
  const [passengers, setPassengers] = useState([emptyPassenger]);
  const [contact, setContact] = useState({ email: "", phone: "" });
  const [payment, setPayment] = useState({ method: "card", cardName: "", cardNumber: "", expiry: "", cvv: "", promo: "" });
  const [accepted, setAccepted] = useState(false);
  const [errors, setErrors] = useState({});
  const [notice, setNotice] = useState("");
  const [apiState, setApiState] = useState({ live: false, label: "Offline reservation mode" });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(reservations));
  }, [reservations]);

  useEffect(() => {
    setPassengers((current) =>
      Array.from({ length: query.passengers }, (_, index) => current[index] || { ...emptyPassenger })
    );
    setSelectedSeats((current) => current.slice(0, query.passengers));
  }, [query.passengers]);

  useEffect(() => {
    let active = true;
    async function checkBackend() {
      for (const base of API_CANDIDATES) {
        try {
          const response = await fetch(`${base}/api/health`);
          if (response.ok && active) {
            setApiState({ live: true, label: `Live operations API ${base}` });
            return;
          }
        } catch {
          // Masar remains fully usable with local reservations when the DSS API is not running.
        }
      }
    }
    checkBackend();
    return () => {
      active = false;
    };
  }, []);

  const trips = useMemo(() => makeTripInstances(query, reservations), [query, reservations]);
  const searchErrors = validateSearch(query);
  const availableTrips = trips.filter((trip) => {
    const routeMatches = trip.from === query.from && trip.to === query.to;
    const seatsFit = trip.remaining >= query.passengers;
    const accessibleFit = !query.accessible || trip.tags.includes("Accessible");
    return routeMatches && seatsFit && accessibleFit;
  });
  const selectedTrip =
    availableTrips.find((trip) => trip.id === selectedTripId) || availableTrips[0] || trips[0];
  const totals = useMemo(() => calculateTotals(selectedTrip, query, selectedSeats, passengers, payment.promo), [
    selectedTrip,
    query,
    selectedSeats,
    passengers,
    payment.promo,
  ]);

  function updateQuery(key, value) {
    setQuery((current) => ({ ...current, [key]: value }));
    setNotice("");
  }

  function swapRoute() {
    setQuery((current) => ({ ...current, from: current.to, to: current.from }));
    setSelectedSeats([]);
  }

  function chooseTrip(tripId) {
    setSelectedTripId(tripId);
    setSelectedSeats([]);
    setErrors({});
    setNotice("");
  }

  function toggleSeat(seat) {
    if (selectedTrip.booked.includes(seat)) return;
    setSelectedSeats((current) => {
      if (current.includes(seat)) return current.filter((value) => value !== seat);
      if (current.length >= query.passengers) {
        setNotice(`You can select ${query.passengers} seat${query.passengers > 1 ? "s" : ""} only.`);
        return current;
      }
      setNotice("");
      return [...current, seat].sort((a, b) => a - b);
    });
  }

  function updatePassenger(index, key, value) {
    setPassengers((current) => current.map((passenger, itemIndex) => (itemIndex === index ? { ...passenger, [key]: value } : passenger)));
  }

  function submitReservation(event) {
    event.preventDefault();
    const nextErrors = validateCheckout({ query, selectedTrip, selectedSeats, passengers, contact, payment, accepted });
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) {
      setNotice("Please fix the highlighted details before confirming.");
      return;
    }

    const booking = {
      id: `MSR-${Date.now().toString().slice(-7)}`,
      status: "confirmed",
      tripId: selectedTrip.id,
      from: selectedTrip.from,
      to: selectedTrip.to,
      date: query.departDate,
      returnDate: query.tripType === "round" ? query.returnDate : "",
      depart: selectedTrip.depart,
      arrive: selectedTrip.arrive,
      seats: selectedSeats,
      passengers,
      contact,
      total: totals.total,
      payment: payment.method === "card" ? maskCard(payment.cardNumber) : "Pay at station",
      createdAt: new Date().toISOString(),
    };

    setReservations((current) => [booking, ...current]);
    setNotice(`Reservation ${booking.id} confirmed. Your seats are locked.`);
    setSelectedSeats([]);
    setAccepted(false);
  }

  function cancelReservation(id) {
    setReservations((current) => current.map((reservation) => (reservation.id === id ? { ...reservation, status: "cancelled" } : reservation)));
  }

  return (
    <div className="masar-shell" dir={language === "ar" ? "rtl" : "ltr"}>
      <header className="hero">
        <nav className="top-nav">
          <div className="brand">
            <span><Bus size={26} /></span>
            <div>
              <strong>Masar</strong>
              <small>مسار</small>
            </div>
          </div>
          <div className="nav-actions">
            <button className="icon-button" title="Switch language" onClick={() => setLanguage(language === "en" ? "ar" : "en")}>
              <Languages size={18} />
            </button>
            <span className={apiState.live ? "system-status live" : "system-status"}>
              <span />
              {apiState.label}
            </span>
          </div>
        </nav>

        <div className="hero-grid">
          <section className="hero-copy">
            <span className="pill"><Sparkles size={16} /> Book smart, travel calmly</span>
            <h1>{language === "ar" ? "مسار لحجز رحلات الحافلات" : "Masar bus trip reservations"}</h1>
            <p>
              Search routes, compare departures, reserve exact seats, validate passenger details, and keep every booking receipt in one polished system app.
            </p>
            <div className="hero-stats" aria-label="Masar service indicators">
              <strong>9 cities</strong>
              <strong>24/7 support</strong>
              <strong>Instant seats</strong>
            </div>
          </section>

          <SearchPanel
            query={query}
            updateQuery={updateQuery}
            swapRoute={swapRoute}
            searchErrors={searchErrors}
            resultCount={availableTrips.length}
          />
        </div>
      </header>

      <main className="workspace">
        <section className="results">
          <div className="section-title">
            <div>
              <span className="eyebrow">Available trips</span>
              <h2>Choose your departure</h2>
            </div>
            <button className="text-button" onClick={() => setSelectedSeats([])}>
              <RefreshCw size={16} />
              Reset seats
            </button>
          </div>

          {Object.keys(searchErrors).length > 0 && <Alert tone="danger" title="Search needs attention" body={Object.values(searchErrors)[0]} />}
          {Object.keys(searchErrors).length === 0 && availableTrips.length === 0 && (
            <EmptyState query={query} />
          )}

          <div className="trip-list">
            {availableTrips.map((trip) => (
              <TripCard
                key={trip.id}
                trip={trip}
                selected={trip.id === selectedTrip.id}
                passengers={query.passengers}
                onChoose={() => chooseTrip(trip.id)}
              />
            ))}
          </div>
        </section>

        <aside className="booking-panel">
          <div className="panel-card">
            <div className="section-title compact">
              <div>
                <span className="eyebrow">Seat map</span>
                <h2>{selectedTrip.id}</h2>
              </div>
              <strong>{selectedSeats.length}/{query.passengers}</strong>
            </div>
            <SeatMap trip={selectedTrip} selectedSeats={selectedSeats} onToggle={toggleSeat} />
            <SeatLegend />
            {notice && <Alert tone={notice.includes("confirmed") ? "success" : "warning"} title="Masar notice" body={notice} />}
          </div>
        </aside>

        <form className="checkout" onSubmit={submitReservation} noValidate>
          <div className="section-title">
            <div>
              <span className="eyebrow">Checkout</span>
              <h2>Passenger and payment details</h2>
            </div>
            <div className="secure"><ShieldCheck size={17} /> Secure demo checkout</div>
          </div>

          <div className="checkout-grid">
            <section className="panel-card">
              <h3><UserRound size={18} /> Passengers</h3>
              {passengers.map((passenger, index) => (
                <div className="passenger-row" key={index}>
                  <label>
                    Full name
                    <input
                      value={passenger.name}
                      onChange={(event) => updatePassenger(index, "name", event.target.value)}
                      placeholder="e.g. Sara Ahmed"
                    />
                    {errors[`passenger-${index}-name`] && <small className="field-error">{errors[`passenger-${index}-name`]}</small>}
                  </label>
                  <label>
                    ID / Iqama
                    <input
                      value={passenger.nationalId}
                      onChange={(event) => updatePassenger(index, "nationalId", event.target.value)}
                      placeholder="10 digits"
                      inputMode="numeric"
                    />
                    {errors[`passenger-${index}-id`] && <small className="field-error">{errors[`passenger-${index}-id`]}</small>}
                  </label>
                  <label>
                    Type
                    <select value={passenger.type} onChange={(event) => updatePassenger(index, "type", event.target.value)}>
                      <option value="adult">Adult</option>
                      <option value="student">Student</option>
                      <option value="child">Child</option>
                      <option value="senior">Senior</option>
                    </select>
                  </label>
                </div>
              ))}
            </section>

            <section className="panel-card">
              <h3><CreditCard size={18} /> Contact and payment</h3>
              <div className="form-grid">
                <label>
                  Email
                  <input value={contact.email} onChange={(event) => setContact({ ...contact, email: event.target.value })} placeholder="name@example.com" />
                  {errors.email && <small className="field-error">{errors.email}</small>}
                </label>
                <label>
                  Mobile
                  <input value={contact.phone} onChange={(event) => setContact({ ...contact, phone: event.target.value })} placeholder="+9665xxxxxxxx" />
                  {errors.phone && <small className="field-error">{errors.phone}</small>}
                </label>
                <label>
                  Payment method
                  <select value={payment.method} onChange={(event) => setPayment({ ...payment, method: event.target.value })}>
                    <option value="card">Card</option>
                    <option value="station">Pay at station</option>
                  </select>
                </label>
                <label>
                  Promo
                  <input value={payment.promo} onChange={(event) => setPayment({ ...payment, promo: event.target.value.toUpperCase() })} placeholder="MASAR10" />
                  {errors.promo && <small className="field-error">{errors.promo}</small>}
                </label>
              </div>

              {payment.method === "card" && (
                <div className="form-grid payment-grid">
                  <label>
                    Name on card
                    <input value={payment.cardName} onChange={(event) => setPayment({ ...payment, cardName: event.target.value })} />
                    {errors.cardName && <small className="field-error">{errors.cardName}</small>}
                  </label>
                  <label>
                    Card number
                    <input value={payment.cardNumber} onChange={(event) => setPayment({ ...payment, cardNumber: event.target.value })} inputMode="numeric" />
                    {errors.cardNumber && <small className="field-error">{errors.cardNumber}</small>}
                  </label>
                  <label>
                    Expiry
                    <input value={payment.expiry} onChange={(event) => setPayment({ ...payment, expiry: event.target.value })} placeholder="MM/YY" />
                    {errors.expiry && <small className="field-error">{errors.expiry}</small>}
                  </label>
                  <label>
                    CVV
                    <input value={payment.cvv} onChange={(event) => setPayment({ ...payment, cvv: event.target.value })} inputMode="numeric" />
                    {errors.cvv && <small className="field-error">{errors.cvv}</small>}
                  </label>
                </div>
              )}
            </section>

            <section className="summary-card">
              <h3><ReceiptText size={18} /> Trip summary</h3>
              <SummaryLine label="Route" value={`${selectedTrip.from} to ${selectedTrip.to}`} />
              <SummaryLine label="Date" value={query.departDate} />
              <SummaryLine label="Departure" value={`${selectedTrip.depart} - ${selectedTrip.arrive}`} />
              <SummaryLine label="Seats" value={selectedSeats.length ? selectedSeats.join(", ") : "Select seats"} />
              <SummaryLine label="Passengers" value={String(query.passengers)} />
              <SummaryLine label="Subtotal" value={formatMoney(totals.subtotal)} />
              <SummaryLine label="Discount" value={`-${formatMoney(totals.discount)}`} />
              <SummaryLine label="Fees" value={formatMoney(totals.fees)} />
              <div className="total-line">
                <span>Total</span>
                <strong>{formatMoney(totals.total)}</strong>
              </div>
              <label className="check-row">
                <input type="checkbox" checked={accepted} onChange={(event) => setAccepted(event.target.checked)} />
                I accept the fare rules and passenger information policy.
              </label>
              {errors.accepted && <small className="field-error">{errors.accepted}</small>}
              {errors.seats && <Alert tone="danger" title="Seat selection" body={errors.seats} />}
              <button className="primary-action" type="submit">
                <Ticket size={18} />
                Confirm reservation
              </button>
            </section>
          </div>
        </form>

        <Reservations reservations={reservations} onCancel={cancelReservation} />
      </main>
    </div>
  );
}

function SearchPanel({ query, updateQuery, swapRoute, searchErrors, resultCount }) {
  return (
    <section className="search-card">
      <div className="segment">
        {["one-way", "round"].map((type) => (
          <button key={type} className={query.tripType === type ? "active" : ""} onClick={() => updateQuery("tripType", type)} type="button">
            {type === "one-way" ? "One-way" : "Round trip"}
          </button>
        ))}
      </div>

      <div className="route-fields">
        <label>
          From
          <select value={query.from} onChange={(event) => updateQuery("from", event.target.value)}>
            {cities.map((city) => <option key={city}>{city}</option>)}
          </select>
        </label>
        <button className="swap" onClick={swapRoute} type="button" title="Swap route">
          <ArrowLeftRight size={18} />
        </button>
        <label>
          To
          <select value={query.to} onChange={(event) => updateQuery("to", event.target.value)}>
            {cities.map((city) => <option key={city}>{city}</option>)}
          </select>
        </label>
      </div>

      <div className="form-grid">
        <label>
          Depart
          <input type="date" value={query.departDate} min={tomorrow()} onChange={(event) => updateQuery("departDate", event.target.value)} />
          {searchErrors.departDate && <small className="field-error">{searchErrors.departDate}</small>}
        </label>
        <label className={query.tripType === "one-way" ? "muted-field" : ""}>
          Return
          <input
            type="date"
            value={query.returnDate}
            min={query.departDate}
            disabled={query.tripType === "one-way"}
            onChange={(event) => updateQuery("returnDate", event.target.value)}
          />
          {searchErrors.returnDate && <small className="field-error">{searchErrors.returnDate}</small>}
        </label>
        <label>
          Passengers
          <div className="stepper">
            <button type="button" onClick={() => updateQuery("passengers", Math.max(1, query.passengers - 1))}><Minus size={16} /></button>
            <strong>{query.passengers}</strong>
            <button type="button" onClick={() => updateQuery("passengers", Math.min(8, query.passengers + 1))}><Plus size={16} /></button>
          </div>
        </label>
        <label>
          Fare
          <select value={query.cabin} onChange={(event) => updateQuery("cabin", event.target.value)}>
            <option value="standard">Standard</option>
            <option value="flex">Flex</option>
            <option value="business">Business</option>
          </select>
        </label>
      </div>

      <label className="check-row">
        <input type="checkbox" checked={query.accessible} onChange={(event) => updateQuery("accessible", event.target.checked)} />
        Accessible boarding required
      </label>

      <div className="search-footer">
        <span><Search size={16} /> {resultCount} matching trips</span>
        <span><CalendarDays size={16} /> {query.departDate}</span>
      </div>
      {searchErrors.route && <Alert tone="danger" title="Invalid route" body={searchErrors.route} />}
    </section>
  );
}

function TripCard({ trip, selected, passengers, onChoose }) {
  const almostFull = trip.remaining <= Math.max(3, passengers);
  return (
    <article className={selected ? "trip-card selected" : "trip-card"}>
      <div className="trip-main">
        <div>
          <strong>{trip.depart}</strong>
          <span>{trip.from}</span>
        </div>
        <div className="timeline">
          <small>{trip.duration}</small>
          <span />
        </div>
        <div>
          <strong>{trip.arrive}</strong>
          <span>{trip.to}</span>
        </div>
      </div>
      <div className="trip-meta">
        <span><Bus size={15} /> {trip.id}</span>
        <span><BadgeCheck size={15} /> {trip.rating}</span>
        <span className={almostFull ? "scarce" : ""}><Armchair size={15} /> {trip.remaining} seats</span>
      </div>
      <div className="tag-row">
        {trip.tags.map((tag) => <small key={tag}>{tag}</small>)}
      </div>
      <div className="trip-bottom">
        <strong>{formatMoney(trip.price)}</strong>
        <button type="button" onClick={onChoose}>
          {selected ? "Selected" : "Select"}
          <ChevronRight size={16} />
        </button>
      </div>
    </article>
  );
}

function SeatMap({ trip, selectedSeats, onToggle }) {
  const seats = Array.from({ length: trip.seats }, (_, index) => index + 1);
  return (
    <div className="bus-map" aria-label="Seat map">
      <div className="driver">Driver</div>
      {seats.map((seat) => {
        const booked = trip.booked.includes(seat);
        const selected = selectedSeats.includes(seat);
        const aisle = seat % 4 === 2;
        return (
          <button
            key={seat}
            type="button"
            disabled={booked}
            className={`${booked ? "booked" : ""} ${selected ? "selected" : ""} ${aisle ? "aisle" : ""}`}
            onClick={() => onToggle(seat)}
            title={booked ? `Seat ${seat} unavailable` : `Seat ${seat}`}
          >
            {seat}
          </button>
        );
      })}
    </div>
  );
}

function SeatLegend() {
  return (
    <div className="legend">
      <span><i className="open" /> Available</span>
      <span><i className="selected" /> Selected</span>
      <span><i className="booked" /> Booked</span>
    </div>
  );
}

function Reservations({ reservations, onCancel }) {
  return (
    <section className="reservations">
      <div className="section-title">
        <div>
          <span className="eyebrow">My trips</span>
          <h2>Reservation receipts</h2>
        </div>
      </div>
      {reservations.length === 0 ? (
        <div className="empty-receipt">
          <Ticket size={34} />
          <strong>No reservations yet</strong>
          <p>Your confirmed Masar tickets will appear here.</p>
        </div>
      ) : (
        <div className="receipt-grid">
          {reservations.map((reservation) => (
            <article className={reservation.status === "cancelled" ? "receipt cancelled" : "receipt"} key={reservation.id}>
              <header>
                <div>
                  <strong>{reservation.id}</strong>
                  <span>{reservation.from} to {reservation.to}</span>
                </div>
                <b>{reservation.status}</b>
              </header>
              <SummaryLine label="Date" value={reservation.date} />
              <SummaryLine label="Time" value={`${reservation.depart} - ${reservation.arrive}`} />
              <SummaryLine label="Seats" value={reservation.seats.join(", ")} />
              <SummaryLine label="Passengers" value={String(reservation.passengers.length)} />
              <SummaryLine label="Paid by" value={reservation.payment} />
              <div className="total-line small">
                <span>Total</span>
                <strong>{formatMoney(reservation.total)}</strong>
              </div>
              {reservation.status === "confirmed" && (
                <button className="danger-action" onClick={() => onCancel(reservation.id)} type="button">
                  <Trash2 size={16} />
                  Cancel reservation
                </button>
              )}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

function EmptyState({ query }) {
  return (
    <div className="empty-state">
      <XCircle size={30} />
      <strong>No exact trips found</strong>
      <p>
        Try changing the route, date, passenger count, or accessibility filter. Masar blocks impossible bookings instead of hiding the issue.
      </p>
      <small>{query.from} to {query.to} · {query.passengers} passengers</small>
    </div>
  );
}

function Alert({ tone, title, body }) {
  const Icon = tone === "success" ? CheckCircle2 : tone === "danger" ? AlertCircle : Clock3;
  return (
    <div className={`alert ${tone}`}>
      <Icon size={18} />
      <div>
        <strong>{title}</strong>
        <p>{body}</p>
      </div>
    </div>
  );
}

function SummaryLine({ label, value }) {
  return (
    <div className="summary-line">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function validateSearch(query) {
  const errors = {};
  if (query.from === query.to) errors.route = "Origin and destination must be different.";
  if (!query.departDate || query.departDate < tomorrow()) errors.departDate = "Choose a future departure date.";
  if (query.tripType === "round" && (!query.returnDate || query.returnDate < query.departDate)) {
    errors.returnDate = "Return date must be after the departure date.";
  }
  if (query.passengers < 1 || query.passengers > 8) errors.passengers = "Masar supports 1 to 8 passengers per reservation.";
  return errors;
}

function validateCheckout({ query, selectedTrip, selectedSeats, passengers, contact, payment, accepted }) {
  const errors = validateSearch(query);
  if (!selectedTrip) errors.trip = "Select a trip before checkout.";
  if (selectedSeats.length !== query.passengers) errors.seats = "Select one available seat for each passenger.";
  if (new Set(selectedSeats).size !== selectedSeats.length) errors.seats = "Each seat can only be selected once.";

  passengers.forEach((passenger, index) => {
    if (passenger.name.trim().length < 3) errors[`passenger-${index}-name`] = "Enter the passenger full name.";
    if (!/^\d{10}$/.test(passenger.nationalId.trim())) errors[`passenger-${index}-id`] = "ID must be exactly 10 digits.";
  });

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(contact.email)) errors.email = "Enter a valid email.";
  if (!/^(\+9665|05)\d{8}$/.test(contact.phone.replace(/\s/g, ""))) errors.phone = "Enter a valid Saudi mobile number.";

  if (payment.promo && !["MASAR10", "STUDENT15"].includes(payment.promo)) {
    errors.promo = "Promo code is not valid.";
  }

  if (payment.method === "card") {
    if (payment.cardName.trim().length < 3) errors.cardName = "Enter the cardholder name.";
    if (!luhn(payment.cardNumber)) errors.cardNumber = "Card number is not valid.";
    if (!/^(0[1-9]|1[0-2])\/\d{2}$/.test(payment.expiry)) errors.expiry = "Use MM/YY format.";
    if (!/^\d{3,4}$/.test(payment.cvv)) errors.cvv = "CVV must be 3 or 4 digits.";
  }

  if (!accepted) errors.accepted = "Accept the fare rules before confirming.";
  return errors;
}

function calculateTotals(trip, query, selectedSeats, passengers, promo) {
  const cabinMultiplier = { standard: 1, flex: 1.18, business: 1.42 }[query.cabin] || 1;
  const passengerTotal = passengers.reduce((sum, passenger) => {
    const discount = { adult: 1, student: 0.85, child: 0.55, senior: 0.7 }[passenger.type] || 1;
    return sum + trip.price * cabinMultiplier * discount;
  }, 0);
  const roundMultiplier = query.tripType === "round" ? 1.92 : 1;
  const subtotal = Math.round(passengerTotal * roundMultiplier);
  const promoDiscount = promo === "MASAR10" ? 0.1 : promo === "STUDENT15" ? 0.15 : 0;
  const discount = Math.round(subtotal * promoDiscount);
  const fees = selectedSeats.length > 0 ? 8 + selectedSeats.length * 3 : 0;
  return { subtotal, discount, fees, total: Math.max(0, subtotal - discount + fees) };
}

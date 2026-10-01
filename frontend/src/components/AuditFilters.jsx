// Child component: the parent owns the filters, and we send every change back UP through onChange
export default function AuditFilters({ filters, onChange, onApply, onReset }) {
  const set = (field) => (e) => onChange({ ...filters, [field]: e.target.value });

  return (
    <form
      className="filters"
      onSubmit={(e) => {
        e.preventDefault();
        onApply();
      }}
    >
      <div>
        <label htmlFor="status">Status</label>
        <select id="status" value={filters.status} onChange={set("status")}>
          <option value="">All</option>
          <option value="FAILED">Failed</option>
          <option value="SUCCESS">Success</option>
        </select>
      </div>
      <div>
        <label htmlFor="action">Action</label>
        <select id="action" value={filters.action} onChange={set("action")}>
          <option value="">All</option>
          <option value="DEPOSIT">Deposit</option>
          <option value="WITHDRAW">Withdraw</option>
          <option value="TRANSFER">Transfer</option>
        </select>
      </div>
      <div>
        <label htmlFor="accountId">Account ID</label>
        <input id="accountId" type="number" min="1" placeholder="Any" value={filters.accountId} onChange={set("accountId")} />
      </div>
      <div className="filter-actions">
        <button className="btn btn-primary" type="submit">Apply</button>
        <button className="btn" type="button" onClick={onReset}>Reset</button>
      </div>
    </form>
  );
}

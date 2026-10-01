// Child component: the parent passes `value` down, and we send changes back UP through onSearch
export default function SearchBar({ value, onSearch, placeholder = "Search..." }) {
  return (
    <div className="search-bar">
      <input
        type="search"
        value={value}
        placeholder={placeholder}
        aria-label={placeholder}
        onChange={(e) => onSearch(e.target.value)}
      />
      {value && (
        <button className="btn" type="button" onClick={() => onSearch("")}>Clear</button>
      )}
    </div>
  );
}

export default function Spinner({ message = "Loading..." }) {
  return (
    <div className="spinner-wrap" role="status">
      <div className="spinner" aria-hidden="true" />
      <span>{message}</span>
    </div>
  );
}

import { formatDate } from "../services/dataService.js";

// Child component: `customers` comes DOWN from the parent as a prop,
// and clicks go back UP to the parent through the onView and onDelete callbacks
export default function CustomerTable({ customers, onView, onDelete }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Joined</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {customers.map((c) => (
            <tr key={c.userId}>
              <td>#{c.userId}</td>
              <td>{c.name}</td>
              <td>{c.email}</td>
              <td>{formatDate(c.createdAt)}</td>
              <td className="row-actions">
                <button className="btn btn-small" onClick={() => onView(c)}>View</button>
                <button className="btn btn-small btn-danger" onClick={() => onDelete(c)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function StatusBadge({ status }) {
  if (!status) {
    return (
      <span className="badge badge-pending">
        <span className="badge-dot"></span>
        <span>Pending</span>
      </span>
    );
  }

  const normalized = status.toLowerCase();
  let badgeClass = 'badge-pending';
  let label = status.replace('_', ' ');

  switch (normalized) {
    case 'pending':
    case 'open':
    case 'broadcasting':
      badgeClass = 'badge-pending';
      label = 'Pending';
      break;
    case 'assigned':
    case 'allocated':
      badgeClass = 'badge-assigned';
      label = 'Assigned';
      break;
    case 'accepted':
      badgeClass = 'badge-accepted';
      label = 'Accepted';
      break;
    case 'en_route':
      badgeClass = 'badge-en_route';
      label = 'En Route';
      break;
    case 'arrived':
      badgeClass = 'badge-arrived';
      label = 'Arrived';
      break;
    case 'in_progress':
      badgeClass = 'badge-in_progress';
      label = 'In Progress';
      break;
    case 'completed':
    case 'fulfilled':
      badgeClass = 'badge-completed';
      label = 'Completed';
      break;
    case 'cancelled':
    case 'rejected':
      badgeClass = 'badge-cancelled';
      label = 'Cancelled';
      break;
    default:
      badgeClass = 'badge-pending';
  }

  return (
    <span className={`badge ${badgeClass}`}>
      <span className="badge-dot"></span>
      <span>{label}</span>
    </span>
  );
}

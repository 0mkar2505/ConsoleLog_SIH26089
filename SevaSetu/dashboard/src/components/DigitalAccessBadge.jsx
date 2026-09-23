import { Smartphone, MessageSquare, PhoneCall } from 'lucide-react';

export default function DigitalAccessBadge({ access }) {
  if (!access || !Array.isArray(access) || access.length === 0) {
    return (
      <span className="channel-tag smartphone">
        <Smartphone size={12} strokeWidth={1.8} />
        <span>Smartphone</span>
      </span>
    );
  }

  return (
    <div style={{ display: 'inline-flex', flexWrap: 'wrap', gap: '0.25rem' }}>
      {access.map((ch) => {
        const cLower = String(ch).toLowerCase();
        let Icon = Smartphone;
        let label = 'Smartphone';

        if (cLower === 'sms') {
          Icon = MessageSquare;
          label = 'SMS';
        } else if (cLower === 'voice') {
          Icon = PhoneCall;
          label = 'Voice';
        }

        return (
          <span key={ch} className={`channel-tag ${cLower}`}>
            <Icon size={11} strokeWidth={1.8} />
            <span>{label}</span>
          </span>
        );
      })}
    </div>
  );
}

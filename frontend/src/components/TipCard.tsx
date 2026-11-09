type Props = {
  tip: string;
  title?: string;
};

export function TipCard({ tip, title = 'Bean Guide' }: Props) {
  return (
    <aside className="panel tip-card">
      <div className="guide-avatar" aria-hidden>
        BG
      </div>
      <div>
        <h2>{title}</h2>
        <p>{tip}</p>
      </div>
    </aside>
  );
}

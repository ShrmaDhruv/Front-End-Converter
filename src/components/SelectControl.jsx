export function SelectControl({ label, value, options, onChange, color }) {
  return (
    <label className="select-control" style={{ "--accent": color }}>
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

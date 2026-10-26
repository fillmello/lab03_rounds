import { InputHTMLAttributes } from "react";

type FieldProps = { label: string; wide?: boolean } & InputHTMLAttributes<HTMLInputElement>;

export function Field({ label, wide = false, required = true, ...input }: FieldProps) {
  return (
    <label className={wide ? "span-two" : ""}>
      {label}
      <input {...input} required={required} />
    </label>
  );
}

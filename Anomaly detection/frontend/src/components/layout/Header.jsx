export default function Header({ title, subtitle }) {
  return (
    <div className="mb-8">
      <h1 className="text-3xl font-extrabold bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
        {title}
      </h1>
      {subtitle && (
        <p className="text-slate-400 mt-2 text-base">{subtitle}</p>
      )}
      <div className="mt-4 h-px bg-gradient-to-r from-indigo-500/50 via-purple-500/30 to-transparent" />
    </div>
  );
}

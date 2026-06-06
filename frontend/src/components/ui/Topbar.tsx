type TopbarProps = {
  title: string
  canSave?: boolean
  saveMessage?: string
  saveError?: string
  onSave?: () => void
}

function Topbar({
  title,
  canSave = false,
  saveMessage = '',
  saveError = '',
  onSave,
}: TopbarProps) {
  return (
    <header className="topbar">
      <div>
        <h1>{title}</h1>
        <p>Geo Mini</p>
      </div>
      <div className="topbar-actions">
        {canSave && onSave && (
          <button type="button" className="topbar-save-button" onClick={onSave}>
            Сохранить
          </button>
        )}
        {saveMessage && <span className="topbar-save-message">{saveMessage}</span>}
        {saveError && <span className="topbar-save-error">{saveError}</span>}
      </div>
    </header>
  )
}

export default Topbar

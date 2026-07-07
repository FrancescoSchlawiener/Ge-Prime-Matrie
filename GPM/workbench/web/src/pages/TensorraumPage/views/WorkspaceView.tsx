import { t } from "../../../i18n/t";
import type { TensorraumStore } from "../hooks/useTensorraumStore";

interface WorkspaceViewProps {
  store: TensorraumStore;
}

export function WorkspaceView({ store }: WorkspaceViewProps) {
  return (
    <div className="gpm-tensor-workspace">
      <div className="gpm-tensor-panel gpm-tensor-panel--grow">
        <header className="gpm-tensor-panel__head">
          <span>{t("tensorraum.workspace.inputTitle")}</span>
          <span className="gpm-metric__hint">{t("tensorraum.workspace.inputSubtitle")}</span>
        </header>
        <div className="gpm-tensor-panel__body gpm-tensor-panel__body--col">
          <textarea
            className="gpm-textarea gpm-tensor-code-input"
            data-testid="tensorraum-code-input"
            value={store.codeInput}
            placeholder={t("tensorraum.workspace.placeholder")}
            onChange={(e) => store.setCodeInput(e.target.value)}
          />
          <button
            type="button"
            className="gpm-tensor-cta"
            data-testid="tensorraum-canonicalize"
            onClick={store.canonicalizeSnippet}
          >
            {t("tensorraum.workspace.canonicalize")}
          </button>
        </div>
      </div>
      <div className="gpm-tensor-panel gpm-tensor-panel--log">
        <header className="gpm-tensor-panel__head">
          <span>{t("tensorraum.workspace.logTitle")}</span>
          <span className="gpm-metric__hint">{t("tensorraum.workspace.logActive")}</span>
        </header>
        <div className="gpm-tensor-panel__body gpm-tensor-log custom-scrollbar">
          {store.logs.map((entry) => (
            <div key={entry.id} className="gpm-tensor-log__line">
              {entry.message}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

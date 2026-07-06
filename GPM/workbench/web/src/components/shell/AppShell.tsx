import { NavLink, Outlet, useLocation } from "react-router-dom";
import { t } from "../../i18n/t";

const TABS = [
  { to: "/codec/encodieren", labelKey: "shell.tabs.codec", prefix: "/codec", testId: "nav-codec" },
  {
    to: "/vergleichen/wortpaar",
    labelKey: "shell.tabs.compare",
    prefix: "/vergleichen",
    testId: "nav-vergleichen",
  },
  { to: "/gpm", labelKey: "shell.tabs.gpm", gpm: true, testId: "nav-gpm" },
  { to: "/datenbank", labelKey: "shell.tabs.database", testId: "nav-datenbank" },
  { to: "/erklaerungen/00-einstieg", labelKey: "shell.tabs.explain", testId: "nav-erklaerungen" },
] as const;

export function AppShell() {
  const location = useLocation();
  const wideExplain = location.pathname.includes("/erklaerungen");
  const wideGpm = location.pathname.startsWith("/gpm");

  return (
    <div className="gpm-app">
      <header className="gpm-header">
        <h1 className="gpm-header__title">{t("shell.brand")}</h1>
        <p className="gpm-header__tagline">{t("shell.tagline")}</p>
        <p className="gpm-header__formula">{t("shell.formulaHero")}</p>
        <nav className="gpm-tabs" aria-label="Hauptnavigation">
          {TABS.map((tab) => (
            <NavLink
              key={tab.to}
              to={tab.to}
              data-testid={tab.testId}
                className={({ isActive }) => {
                  const tabActive =
                    "prefix" in tab && tab.prefix ? location.pathname.startsWith(tab.prefix) : isActive;
                  return [
                    "gpm-tab",
                    "gpm" in tab && tab.gpm ? "gpm-tab--gpm" : "",
                    tabActive ? "gpm-tab--active" : "",
                  ]
                    .filter(Boolean)
                    .join(" ");
                }}
              >
                {t(tab.labelKey)}
              </NavLink>
          ))}
        </nav>
      </header>
      <main
        className={[
          "gpm-main",
          wideExplain ? "gpm-main--wide" : "",
          wideGpm ? "gpm-main--gpm" : "",
        ]
          .filter(Boolean)
          .join(" ")}
      >
        <Outlet />
      </main>
      <footer className="gpm-footer">{t("shell.footer.libraryRef")}</footer>
    </div>
  );
}

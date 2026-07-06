import { lazy, Suspense } from "react";
import { HashRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "./components/shell/AppShell";
import { CodecPage } from "./pages/CodecPage/CodecPage";
import { DecodeView } from "./pages/CodecPage/DecodeView/DecodeView";
import { EncodeView } from "./pages/CodecPage/EncodeView/EncodeView";
import { DatenbankPage } from "./pages/DatenbankPage/DatenbankPage";
import { ErklaerungenPage } from "./pages/ErklaerungenPage";
import { VergleichenPage } from "./pages/VergleichenPage/VergleichenPage";
import { WortpaarView } from "./pages/VergleichenPage/WortpaarView/WortpaarView";

const GpmPage = lazy(() => import("./pages/GpmPage/GpmPage").then((m) => ({ default: m.GpmPage })));
const ICurveView = lazy(() =>
  import("./pages/VergleichenPage/ICurveView/ICurveView").then((m) => ({ default: m.ICurveView })),
);

function LegacyRedirect({ to }: { to: string }) {
  return <Navigate to={to} replace />;
}

export function App() {
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<AppShell />}>
          <Route index element={<Navigate to="/codec/encodieren" replace />} />
          <Route path="codec" element={<CodecPage />}>
            <Route index element={<Navigate to="encodieren" replace />} />
            <Route path="encodieren" element={<EncodeView />} />
            <Route path="decodieren" element={<DecodeView />} />
          </Route>
          <Route path="vergleichen" element={<VergleichenPage />}>
            <Route index element={<Navigate to="wortpaar" replace />} />
            <Route path="wortpaar" element={<WortpaarView />} />
            <Route
              path="ikurve"
              element={
                <Suspense fallback={<p className="gpm-empty">…</p>}>
                  <ICurveView />
                </Suspense>
              }
            />
          </Route>
          <Route
            path="gpm"
            element={
              <Suspense fallback={<p className="gpm-empty">…</p>}>
                <GpmPage />
              </Suspense>
            }
          />
          <Route path="datenbank" element={<DatenbankPage />} />
          <Route path="erklaerungen" element={<Navigate to="/erklaerungen/00-einstieg" replace />} />
          <Route path="erklaerungen/:chapter" element={<ErklaerungenPage />} />
          {/* Legacy */}
          <Route path="encodieren" element={<LegacyRedirect to="/codec/encodieren" />} />
          <Route path="decodieren" element={<LegacyRedirect to="/codec/decodieren" />} />
          <Route path="wortpaar" element={<LegacyRedirect to="/vergleichen/wortpaar" />} />
          <Route path="ikurve" element={<LegacyRedirect to="/vergleichen/ikurve" />} />
          <Route path="editor" element={<LegacyRedirect to="/gpm" />} />
          <Route path="editor/:mode" element={<LegacyRedirect to="/gpm" />} />
        </Route>
      </Routes>
    </HashRouter>
  );
}

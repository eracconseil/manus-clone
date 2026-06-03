"use client";
import { useState } from "react";
import { Zap, Send, LayoutDashboard, Search, Code, FileText } from "lucide-react";

const THEMES = {
  obsidian: {
    name: "Obsidian & Or",
    subtitle: "Rolex · Cartier",
    bg: "#080808",
    bgCard: "#0f0f0f",
    border: "#2a2200",
    accent: "#C9A84C",
    accentSoft: "#F5E6C8",
    accentGlow: "rgba(201,168,76,0.15)",
    text: "#F5E6C8",
    textMuted: "#7a6a4a",
    userBg: "#1a1400",
    userBorder: "#C9A84C",
    aiBg: "#0f0f0f",
    aiBorder: "#2a2200",
    inputBg: "#0f0f0f",
    badge: "#1a1400",
    badgeBorder: "#C9A84C",
    badgeText: "#C9A84C",
    buttonGrad: "linear-gradient(135deg, #C9A84C, #8B6914)",
    shimmer: true,
  },
  midnight: {
    name: "Midnight Glass",
    subtitle: "Apple Vision · Linear",
    bg: "#050510",
    bgCard: "rgba(255,255,255,0.04)",
    border: "rgba(77,124,255,0.15)",
    accent: "#4D7CFF",
    accentSoft: "#ffffff",
    accentGlow: "rgba(77,124,255,0.2)",
    text: "#ffffff",
    textMuted: "#5a6a8a",
    userBg: "rgba(77,124,255,0.12)",
    userBorder: "rgba(77,124,255,0.3)",
    aiBg: "rgba(255,255,255,0.04)",
    aiBorder: "rgba(255,255,255,0.08)",
    inputBg: "rgba(255,255,255,0.05)",
    badge: "rgba(77,124,255,0.15)",
    badgeBorder: "rgba(77,124,255,0.4)",
    badgeText: "#4D7CFF",
    buttonGrad: "linear-gradient(135deg, #4D7CFF, #2952cc)",
    shimmer: false,
  },
  onyx: {
    name: "Onyx & Améthyste",
    subtitle: "Notion AI · Perplexity",
    bg: "#09080F",
    bgCard: "#0e0c18",
    border: "#1e1830",
    accent: "#8B5CF6",
    accentSoft: "#C4B5FD",
    accentGlow: "rgba(139,92,246,0.2)",
    text: "#e8e4f8",
    textMuted: "#6b6485",
    userBg: "rgba(139,92,246,0.1)",
    userBorder: "rgba(139,92,246,0.3)",
    aiBg: "#0e0c18",
    aiBorder: "#1e1830",
    inputBg: "#0e0c18",
    badge: "rgba(139,92,246,0.15)",
    badgeBorder: "rgba(139,92,246,0.4)",
    badgeText: "#8B5CF6",
    buttonGrad: "linear-gradient(135deg, #8B5CF6, #6d28d9)",
    shimmer: false,
  },
  creme: {
    name: "Crème & Noir",
    subtitle: "Bottega Veneta · Loro Piana",
    bg: "#F8F5EF",
    bgCard: "#ffffff",
    border: "#e8e0d0",
    accent: "#8B6914",
    accentSoft: "#0D0D0D",
    accentGlow: "rgba(139,105,20,0.1)",
    text: "#0D0D0D",
    textMuted: "#8a7a6a",
    userBg: "#0D0D0D",
    userBorder: "#0D0D0D",
    aiBg: "#ffffff",
    aiBorder: "#e8e0d0",
    inputBg: "#ffffff",
    badge: "#f0e8d8",
    badgeBorder: "#8B6914",
    badgeText: "#8B6914",
    buttonGrad: "linear-gradient(135deg, #0D0D0D, #2a2a2a)",
    shimmer: false,
  },
};

type ThemeKey = keyof typeof THEMES;

function ThemePreview({ themeKey, active, onClick }: { themeKey: ThemeKey; active: boolean; onClick: () => void }) {
  const t = THEMES[themeKey];
  const isLight = themeKey === "creme";

  return (
    <div
      onClick={onClick}
      style={{
        cursor: "pointer",
        border: active ? `2px solid ${t.accent}` : "2px solid transparent",
        borderRadius: 20,
        overflow: "hidden",
        transition: "all 0.3s",
        transform: active ? "scale(1.01)" : "scale(1)",
        boxShadow: active ? `0 0 40px ${t.accentGlow}` : "none",
      }}
    >
      {/* Mini app preview */}
      <div style={{ background: t.bg, height: 480, display: "flex", flexDirection: "column" }}>
        {/* Header */}
        <div style={{
          display: "flex", alignItems: "center", justifyContent: "space-between",
          padding: "12px 16px", borderBottom: `1px solid ${t.border}`,
          background: themeKey === "midnight" ? "rgba(255,255,255,0.03)" : t.bg,
          backdropFilter: themeKey === "midnight" ? "blur(20px)" : "none",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{
              width: 28, height: 28, borderRadius: 8,
              background: t.buttonGrad,
              display: "flex", alignItems: "center", justifyContent: "center",
              boxShadow: `0 0 16px ${t.accentGlow}`,
            }}>
              <Zap size={13} color={isLight ? "#fff" : "#fff"} />
            </div>
            <span style={{
              fontWeight: 700, fontSize: 13, color: t.text,
              fontFamily: "'Georgia', serif",
              letterSpacing: 1,
            }}>ORION</span>
            <span style={{
              fontSize: 9, padding: "1px 8px", borderRadius: 20,
              background: t.badge, border: `1px solid ${t.badgeBorder}`,
              color: t.badgeText, letterSpacing: 1, textTransform: "uppercase",
            }}>BETA</span>
          </div>
          <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
            <span style={{ fontSize: 9, color: t.textMuted }}>Claude · Kimi · Qwen</span>
            <LayoutDashboard size={13} color={t.textMuted} />
          </div>
        </div>

        {/* Messages area */}
        <div style={{ flex: 1, padding: "16px", display: "flex", flexDirection: "column", gap: 10, overflowY: "hidden" }}>
          {/* AI message */}
          <div style={{ display: "flex", gap: 8, alignItems: "flex-start" }}>
            <div style={{
              width: 22, height: 22, borderRadius: 6, flexShrink: 0,
              background: t.buttonGrad,
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <Zap size={10} color="#fff" />
            </div>
            <div style={{
              background: themeKey === "midnight" ? "rgba(255,255,255,0.04)" : t.aiBg,
              border: `1px solid ${t.aiBorder}`,
              borderRadius: "4px 12px 12px 12px",
              padding: "8px 12px", maxWidth: "75%",
              backdropFilter: themeKey === "midnight" ? "blur(10px)" : "none",
            }}>
              <p style={{ fontSize: 10, color: t.text, margin: 0, lineHeight: 1.6 }}>
                Bonjour, je suis <strong style={{ color: t.accent }}>Orion</strong>. Comment puis-je vous assister aujourd'hui ?
              </p>
            </div>
          </div>

          {/* User message */}
          <div style={{ display: "flex", justifyContent: "flex-end" }}>
            <div style={{
              background: themeKey === "creme" ? t.userBg : t.userBg,
              border: `1px solid ${t.userBorder}`,
              borderRadius: "12px 4px 12px 12px",
              padding: "8px 12px", maxWidth: "70%",
            }}>
              <p style={{ fontSize: 10, color: themeKey === "creme" ? "#fff" : t.accentSoft, margin: 0, lineHeight: 1.6 }}>
                Analyse ce marché et rédige un rapport complet
              </p>
            </div>
          </div>

          {/* Tool call card */}
          <div style={{ display: "flex", gap: 8, alignItems: "flex-start" }}>
            <div style={{ width: 22, height: 22, borderRadius: 6, flexShrink: 0, background: t.buttonGrad, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Zap size={10} color="#fff" />
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 4, maxWidth: "75%" }}>
              <div style={{
                background: t.accentGlow, border: `1px solid ${t.badgeBorder}`,
                borderRadius: 8, padding: "5px 10px",
                display: "flex", alignItems: "center", gap: 6,
              }}>
                <Search size={9} color={t.accent} />
                <span style={{ fontSize: 9, color: t.accent }}>web_search · "analyse marché IA 2025"</span>
              </div>
              <div style={{
                background: t.accentGlow, border: `1px solid ${t.badgeBorder}`,
                borderRadius: 8, padding: "5px 10px",
                display: "flex", alignItems: "center", gap: 6,
              }}>
                <FileText size={9} color={t.accent} />
                <span style={{ fontSize: 9, color: t.accent }}>file_write · rapport_marche.md</span>
              </div>
              <div style={{
                background: themeKey === "midnight" ? "rgba(255,255,255,0.04)" : t.aiBg,
                border: `1px solid ${t.aiBorder}`,
                borderRadius: "4px 12px 12px 12px",
                padding: "8px 12px",
              }}>
                <p style={{ fontSize: 10, color: t.text, margin: 0, lineHeight: 1.6 }}>
                  Rapport généré avec <span style={{ color: t.accent }}>42 sources analysées</span>. Fichier disponible dans votre espace.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Input */}
        <div style={{ padding: "10px 12px", borderTop: `1px solid ${t.border}` }}>
          <div style={{
            display: "flex", alignItems: "center", gap: 8,
            background: themeKey === "midnight" ? "rgba(255,255,255,0.05)" : t.inputBg,
            border: `1px solid ${t.border}`,
            borderRadius: 12, padding: "8px 12px",
            backdropFilter: themeKey === "midnight" ? "blur(10px)" : "none",
          }}>
            <span style={{ fontSize: 10, color: t.textMuted, flex: 1 }}>Demandez à Orion...</span>
            <div style={{
              width: 22, height: 22, borderRadius: 6, background: t.buttonGrad,
              display: "flex", alignItems: "center", justifyContent: "center",
              boxShadow: `0 0 12px ${t.accentGlow}`,
            }}>
              <Send size={9} color="#fff" />
            </div>
          </div>
        </div>
      </div>

      {/* Label */}
      <div style={{
        background: t.bg, borderTop: `1px solid ${t.border}`,
        padding: "12px 16px", display: "flex", alignItems: "center", justifyContent: "space-between",
      }}>
        <div>
          <p style={{ margin: 0, fontWeight: 700, fontSize: 13, color: t.text }}>{t.name}</p>
          <p style={{ margin: 0, fontSize: 11, color: t.textMuted, marginTop: 2 }}>{t.subtitle}</p>
        </div>
        {active && (
          <div style={{
            padding: "4px 12px", borderRadius: 20,
            background: t.buttonGrad, fontSize: 10, color: "#fff", fontWeight: 700,
          }}>
            SÉLECTIONNÉ
          </div>
        )}
      </div>
    </div>
  );
}

export default function ThemesPage() {
  const [selected, setSelected] = useState<ThemeKey | null>(null);

  return (
    <div style={{ minHeight: "100vh", background: "#030308", padding: "40px 24px" }}>
      {/* Title */}
      <div style={{ textAlign: "center", marginBottom: 48 }}>
        <h1 style={{
          fontSize: 36, fontWeight: 800, color: "#fff",
          fontFamily: "'Georgia', serif", letterSpacing: 2, marginBottom: 8,
        }}>
          Choisissez votre design
        </h1>
        <p style={{ color: "#555", fontSize: 14 }}>Cliquez sur un thème pour le sélectionner</p>
      </div>

      {/* Grid */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
        gap: 24, maxWidth: 1400, margin: "0 auto",
      }}>
        {(Object.keys(THEMES) as ThemeKey[]).map((key) => (
          <ThemePreview
            key={key}
            themeKey={key}
            active={selected === key}
            onClick={() => setSelected(key)}
          />
        ))}
      </div>

      {/* CTA */}
      {selected && (
        <div style={{ textAlign: "center", marginTop: 48 }}>
          <div style={{
            display: "inline-flex", flexDirection: "column", alignItems: "center", gap: 8,
            background: "#0e0e1a", border: "1px solid #1e1e2e",
            borderRadius: 16, padding: "20px 40px",
          }}>
            <p style={{ color: "#888", fontSize: 13, margin: 0 }}>Thème sélectionné</p>
            <p style={{ color: "#fff", fontSize: 20, fontWeight: 700, margin: 0 }}>
              {THEMES[selected].name}
            </p>
            <p style={{ color: "#555", fontSize: 12, margin: 0 }}>
              Dites "applique ce thème" et je l'intègre dans toute l'app
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

"use client";

import { useEffect, useRef, useState } from "react";
import type { CandidacyDetail, ClaimRead, PromiseRead } from "@/lib/types";

type NodeData =
  | { type: "person"; id: string; label: string }
  | { type: "party"; id: string; label: string }
  | { type: "promise"; id: string; label: string; item: PromiseRead }
  | { type: "claim"; id: string; label: string; item: ClaimRead };

interface CandidateGraphProps {
  candidacy: CandidacyDetail;
  onNodeClick?: (node: NodeData) => void;
}

const NODE_COLORS: Record<string, string> = {
  person: "#3b82f6",
  party: "#8b5cf6",
  promise: "#22c55e",
  claim: "#f59e0b",
};

const NODE_LABELS_KO: Record<string, string> = {
  person: "인물",
  party: "정당",
  promise: "공약",
  claim: "주장",
};

const CLAIM_TYPE_KO: Record<string, string> = {
  fact: "사실",
  promise_check: "공약 검증",
  allegation: "의혹",
  denial: "부인",
  support: "지지",
  criticism: "비판",
};

function MobileListView({
  candidacy,
  onItemClick,
}: {
  candidacy: CandidacyDetail;
  onItemClick?: (node: NodeData) => void;
}) {
  return (
    <div className="space-y-4">
      {candidacy.party && (
        <div>
          <h4 className="mb-2 text-xs font-bold uppercase tracking-wider text-purple-600">
            소속 정당
          </h4>
          <button
            onClick={() =>
              onItemClick?.({
                type: "party",
                id: candidacy.party!.id,
                label: candidacy.party!.name_ko,
              })
            }
            className="w-full rounded-xl border-2 border-purple-200 bg-purple-50 px-4 py-3 text-left transition hover:border-purple-300"
          >
            <span className="font-semibold text-purple-800">
              {candidacy.party.name_ko}
            </span>
          </button>
        </div>
      )}

      {candidacy.promises.length > 0 && (
        <div>
          <h4 className="mb-2 text-xs font-bold uppercase tracking-wider text-green-600">
            핵심 공약 (상위 5개)
          </h4>
          <div className="space-y-2">
            {candidacy.promises.slice(0, 5).map((p) => (
              <button
                key={p.id}
                onClick={() =>
                  onItemClick?.({
                    type: "promise",
                    id: p.id,
                    label: p.title,
                    item: p,
                  })
                }
                className="w-full rounded-xl border-2 border-green-200 bg-green-50 px-4 py-3 text-left transition hover:border-green-300"
              >
                <span className="line-clamp-2 text-sm font-medium text-green-800">
                  {p.title}
                </span>
                {p.category && (
                  <span className="mt-1 block text-xs text-green-600">
                    {p.category}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {candidacy.claims.length > 0 && (
        <div>
          <h4 className="mb-2 text-xs font-bold uppercase tracking-wider text-amber-600">
            관련 주장
          </h4>
          <div className="space-y-2">
            {candidacy.claims.map((c) => (
              <button
                key={c.id}
                onClick={() =>
                  onItemClick?.({
                    type: "claim",
                    id: c.id,
                    label: c.content.slice(0, 40) + (c.content.length > 40 ? "…" : ""),
                    item: c,
                  })
                }
                className="w-full rounded-xl border-2 border-amber-200 bg-amber-50 px-4 py-3 text-left transition hover:border-amber-300"
              >
                <span className="mb-1 block text-xs font-bold text-amber-700">
                  {CLAIM_TYPE_KO[c.claim_type] ?? c.claim_type}
                </span>
                <span className="line-clamp-2 text-sm text-amber-800">
                  {c.content}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export function CandidateGraph({ candidacy, onNodeClick }: CandidateGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<import("cytoscape").Core | null>(null);
  const [isMobile, setIsMobile] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  useEffect(() => {
    if (!mounted || isMobile || !containerRef.current) return;

    let cy: import("cytoscape").Core | null = null;

    const initCy = async () => {
      const cytoscape = (await import("cytoscape")).default;

      const elements: import("cytoscape").ElementDefinition[] = [];

      const personId = `person-${candidacy.person_id}`;
      elements.push({
        data: {
          id: personId,
          label: candidacy.person.name_ko,
          nodeType: "person",
        },
      });

      if (candidacy.party) {
        const partyId = `party-${candidacy.party.id}`;
        elements.push({
          data: {
            id: partyId,
            label: candidacy.party.name_ko,
            nodeType: "party",
          },
        });
        elements.push({
          data: {
            id: `e-person-party`,
            source: personId,
            target: partyId,
            label: "소속",
          },
        });
      }

      candidacy.promises.slice(0, 5).forEach((p, i) => {
        const nodeId = `promise-${p.id}`;
        const shortTitle = p.title.length > 20 ? p.title.slice(0, 20) + "…" : p.title;
        elements.push({
          data: {
            id: nodeId,
            label: shortTitle,
            nodeType: "promise",
            itemId: p.id,
          },
        });
        elements.push({
          data: {
            id: `e-person-promise-${i}`,
            source: personId,
            target: nodeId,
            label: "공약",
          },
        });
      });

      candidacy.claims.forEach((c, i) => {
        const nodeId = `claim-${c.id}`;
        const shortContent =
          c.content.length > 20 ? c.content.slice(0, 20) + "…" : c.content;
        elements.push({
          data: {
            id: nodeId,
            label: shortContent,
            nodeType: "claim",
            itemId: c.id,
          },
        });
        elements.push({
          data: {
            id: `e-person-claim-${i}`,
            source: personId,
            target: nodeId,
            label: CLAIM_TYPE_KO[c.claim_type] ?? c.claim_type,
          },
        });
      });

      if (!containerRef.current) return;

      cy = cytoscape({
        container: containerRef.current,
        elements,
        style: [
          {
            selector: "node",
            style: {
              "background-color": (ele) =>
                NODE_COLORS[ele.data("nodeType") as string] ?? "#94a3b8",
              label: "data(label)",
              "text-valign": "center",
              "text-halign": "center",
              color: "#ffffff",
              "font-size": "11px",
              "font-weight": 600,
              "text-wrap": "wrap",
              "text-max-width": "80px",
              width: "label",
              height: "label",
              padding: "10px",
              shape: "round-rectangle",
              "border-width": 0,
            },
          },
          {
            selector: `node[nodeType = "person"]`,
            style: {
              width: 80,
              height: 80,
              shape: "ellipse",
              "font-size": "13px",
              "font-weight": 700,
            },
          },
          {
            selector: "edge",
            style: {
              width: 2,
              "line-color": "#cbd5e1",
              "target-arrow-color": "#cbd5e1",
              "target-arrow-shape": "triangle",
              "curve-style": "bezier",
              label: "data(label)",
              "font-size": "9px",
              color: "#94a3b8",
              "text-rotation": "autorotate",
            },
          },
          {
            selector: "node:selected",
            style: {
              "border-width": 3,
              "border-color": "#1e293b",
            },
          },
        ],
        layout: {
          name: "cose",
          animate: true,
          animationDuration: 500,
          nodeRepulsion: () => 8000,
          idealEdgeLength: () => 120,
          gravity: 0.2,
        },
        minZoom: 0.5,
        maxZoom: 2,
        wheelSensitivity: 0.3,
      });

      cy.on("tap", "node", (evt) => {
        const node = evt.target;
        const nodeType = node.data("nodeType") as string;
        const nodeId: string = node.data("id") as string;
        const label: string = node.data("label") as string;
        const itemId: string | undefined = node.data("itemId") as string | undefined;

        if (nodeType === "person") {
          onNodeClick?.({ type: "person", id: nodeId, label });
        } else if (nodeType === "party" && candidacy.party) {
          onNodeClick?.({
            type: "party",
            id: candidacy.party.id,
            label: candidacy.party.name_ko,
          });
        } else if (nodeType === "promise" && itemId) {
          const promise = candidacy.promises.find((p) => p.id === itemId);
          if (promise) {
            onNodeClick?.({ type: "promise", id: itemId, label, item: promise });
          }
        } else if (nodeType === "claim" && itemId) {
          const claim = candidacy.claims.find((c) => c.id === itemId);
          if (claim) {
            onNodeClick?.({ type: "claim", id: itemId, label, item: claim });
          }
        }
      });

      cyRef.current = cy;
    };

    initCy().catch(console.error);

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [mounted, isMobile, candidacy, onNodeClick]);

  useEffect(() => {
    if (!containerRef.current) return;
    const ro = new ResizeObserver(() => {
      cyRef.current?.resize();
      cyRef.current?.fit(undefined, 40);
    });
    ro.observe(containerRef.current);
    return () => ro.disconnect();
  }, []);

  if (!mounted) return null;

  if (isMobile) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-4">
        <h3 className="mb-4 text-sm font-bold text-slate-700">관계 목록</h3>
        <MobileListView candidacy={candidacy} onItemClick={onNodeClick} />
      </div>
    );
  }

  return (
    <div className="relative rounded-2xl border border-slate-200 bg-slate-50 overflow-hidden">
      <div className="absolute right-4 top-4 z-10 flex flex-col gap-1.5 rounded-xl bg-white/90 p-3 shadow-sm backdrop-blur-sm">
        {Object.entries(NODE_COLORS).map(([type, color]) => (
          <div key={type} className="flex items-center gap-2">
            <span
              className="h-3 w-3 rounded-full"
              style={{ backgroundColor: color }}
            />
            <span className="text-xs text-slate-600">
              {NODE_LABELS_KO[type]}
            </span>
          </div>
        ))}
      </div>
      <div
        ref={containerRef}
        className="w-full"
        style={{ minHeight: 400 }}
        aria-label="후보 관계 그래프"
      />
    </div>
  );
}

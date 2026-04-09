"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import {
  getCandidacies,
  getCandidacy,
  getCandidacyClaims,
  getCandidacyPromises,
  getElection,
  getElections,
  getIssue,
  getIssues,
  getPerson,
  getPersons,
  resolveBallot,
  search,
  getCandidaciesByDistrict,
} from "@/lib/api";

export function useBallotResolve() {
  return useMutation({
    mutationFn: (address: string) => resolveBallot(address),
  });
}

export function useElections() {
  return useQuery({
    queryKey: ["elections"],
    queryFn: getElections,
  });
}

export function useElection(id: string) {
  return useQuery({
    queryKey: ["election", id],
    queryFn: () => getElection(id),
    enabled: !!id,
  });
}

export function useCandidacy(id: string) {
  return useQuery({
    queryKey: ["candidacy", id],
    queryFn: () => getCandidacy(id),
    enabled: !!id,
  });
}

export function useCandidacies(params: Record<string, string | number>) {
  return useQuery({
    queryKey: ["candidacies", params],
    queryFn: () => getCandidacies(params),
  });
}

export function useCandidaciesByDistrict(districtId: string) {
  return useQuery({
    queryKey: ["candidacies-by-district", districtId],
    queryFn: () => getCandidaciesByDistrict(districtId),
    enabled: !!districtId,
  });
}

export function useCandidacyPromises(id: string) {
  return useQuery({
    queryKey: ["candidacy-promises", id],
    queryFn: () => getCandidacyPromises(id),
    enabled: !!id,
  });
}

export function useCandidacyClaims(id: string) {
  return useQuery({
    queryKey: ["candidacy-claims", id],
    queryFn: () => getCandidacyClaims(id),
    enabled: !!id,
  });
}

export function usePersons() {
  return useQuery({
    queryKey: ["persons"],
    queryFn: getPersons,
  });
}

export function usePerson(id: string) {
  return useQuery({
    queryKey: ["person", id],
    queryFn: () => getPerson(id),
    enabled: !!id,
  });
}

export function useIssues() {
  return useQuery({
    queryKey: ["issues"],
    queryFn: getIssues,
  });
}

export function useIssue(id: string) {
  return useQuery({
    queryKey: ["issue", id],
    queryFn: () => getIssue(id),
    enabled: !!id,
  });
}

export function useSearch(q: string, type?: string) {
  return useQuery({
    queryKey: ["search", q, type],
    queryFn: () => search(q, type),
    enabled: q.length > 0,
  });
}

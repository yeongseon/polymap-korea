import http from "k6/http";
import { check } from "k6";

const baseUrl = __ENV.K6_BASE_URL || "http://localhost:8000";

export const options = {
  vus: 1,
  iterations: 10,
};

export default function () {
  const health = http.get(`${baseUrl}/api/v1/health`);
  check(health, {
    "health returned 200": (res) => res.status === 200,
  });

  const elections = http.get(`${baseUrl}/api/v1/elections`);
  check(elections, {
    "elections returned 200": (res) => res.status === 200,
  });
}

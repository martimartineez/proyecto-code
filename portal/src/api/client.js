import { API_BASE_URL } from '@/config';

async function httpGet(path, params = {}) {
  const url = new URL(API_BASE_URL + path, window.location.origin);
  Object.entries(params).forEach(([k, v]) => {
    if (v === undefined || v === null || v === '') return;
    if (Array.isArray(v)) {
      v.forEach((vv) => url.searchParams.append(k, vv));
    } else {
      url.searchParams.set(k, v);
    }
  });
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export const api = {
  listSites(params) {
    return httpGet('/sites', params);
  },
  listProvinces() {
    return httpGet('/filters/provinces');
  },
  listCities(params) {
    return httpGet('/filters/cities', params);
  },
  listTags() {
    return httpGet('/filters/tags');
  },
};




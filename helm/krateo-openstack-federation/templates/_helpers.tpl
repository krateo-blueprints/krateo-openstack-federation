{{- define "of.labels" -}}
app.kubernetes.io/name: krateo-openstack-federation
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
{{- end -}}

{{- define "of.configurationRef" -}}
configurationRef:
  name: {{ .Values.configuration.name }}
  namespace: {{ .Release.Namespace }}
{{- end -}}

{{- define "of.check" -}}
{{- if not .Values.identityProvider.issuer -}}
{{- fail "identityProvider.issuer is required: the Keycloak realm's issuer, e.g. https://keycloak.example.com/realms/krateo" -}}
{{- end -}}
{{- if not (hasPrefix "https://" .Values.identityProvider.issuer) -}}
{{- fail "identityProvider.issuer must be an https URL: Keystone trusts the claims of this issuer" -}}
{{- end -}}
{{- if not (regexMatch "^[a-z0-9]([-a-z0-9]*[a-z0-9])?-?$" .Values.tenants.projectPrefix) -}}
{{- fail "tenants.projectPrefix must be lowercase letters, digits and dashes (it prefixes Kubernetes object names)" -}}
{{- end -}}
{{- end -}}

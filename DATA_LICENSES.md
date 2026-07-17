# Data and source-material policy

The repository does not redistribute downloaded clinical guidelines, articles, or patient-education pages. Users must obtain them directly from the original providers and follow their current terms.

The manuscript's source classes are represented in `configs/sources.yaml`: AAOS guidelines, AO Surgery Reference, PubMed Central Open Access, PhysioNet, WikiDoc, and MedlinePlus. The ingestion code records a source URL, access date, license note, and local checksum in the manifest. It refuses to silently treat an unknown source as redistributable.

Synthetic fixtures under `data/examples/` are original test records and contain no patient data. They are included only to exercise the code path.

Before publication or redistribution, the user is responsible for checking:

1. terms of use and license compatibility for each source;
2. robots, API, and rate-limit requirements;
3. removal of credentials, downloaded raw files, and local patient or institutional identifiers;
4. whether generated examples require attribution to the source material or generation provider.

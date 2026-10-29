# Public repository selections

This layer selects exact, verified capture objects from a reviewed **public**
workflow artifact. It does not create a new scan, rewrite a checkpoint, or turn
automatic discovery into individually reviewed recommendations.

`index.json` is an ordered, explicit batch registry. Each registered batch binds
the canonical baseline, an approved public evidence descriptor, ordered numeric
repository IDs, and hashes of the original capture objects. The complete source
archive is checked, including unselected records, the frontier and the receipt.
Unknown source pins, identity conflicts, altered objects, missing comparison
evidence, and Git-hash mismatches are rejected.

The initial 500 candidates use `strong-reverse-engineering-topics-v1`. This is a
bounded metadata screen, not a claim that all projects are useful, safe,
compatible, execution-tested, or integrated with REA. Their 495 nonempty
descriptions require complete English and Simplified Chinese coverage; the five empty
descriptions remain empty. Language completion does not automatically admit a
batch: `held-for-localization` and `held-for-review` both keep it out of website
results and publication counts.

Twenty-six captures have exact README duplicates of two already visible
canonical entries. All 500 capture objects and locales remain intact, while
those 26 are separately excluded from browsing. If admitted, this batch gives
3,500 published records, 190 total exclusions and 3,310 browsable entries.
Supplement scope decisions may affect only new IDs. A duplicate decision can
cite canonical context only when that reference remains visible and has the
same repository name and README SHA-256; it cannot reclassify a baseline row.

## Admission and language review

1. Review candidate IDs and scope using the original public source evidence.
2. Prepare a held selection without modifying the registry:

   ```sh
   python3 scripts/public_source_supplements.py \
     --prepare-batch next-public-batch \
     --source-batch public-cloud-39323601991-batch-01 \
     --ids .cache/reviewed-source-ids.json \
     --output .cache/next-public-batch.json
   ```

3. Review the exact output before adding it to the registry. Duplicate IDs or
   ambiguous repository names across batches are rejected.
4. Add exact per-batch locale coverage under
   `data/locales/source-supplements/<batch-id>.json`. Use the same fields and
   language rules as the canonical [localization layer](../locales/README.md).
   Natural English stays unchanged; other source languages receive a faithful
   English version. Nonempty descriptions need faithful Simplified Chinese.
   Do not invent text for empty or explicitly omitted descriptions.
5. If needed, record separately reviewed exclusions in
   `<batch-id>.scope.json`, using the existing source-scope schema.
6. Only after source/selection and locale review, set the batch to `ready` and
   record the actual timezone-aware `reviewed_at`. Derived publication times and
   displayed dates are normalized to UTC `Z`; the recorded input is retained.
   Validation rejects incomplete
   locale coverage. Translation alone is not publication admission.

Run `python3 scripts/public_source_supplements.py` to check the registry and
report ready versus held counts. It performs no network requests.

## Published outputs

The original canonical `data/source-index.json`, its 3,000 records, failure
history, and existing locales remain unchanged. The existing generated
`/source-index.json` remains that complete canonical export.

When at least one batch is ready, `/source-published.json` is a separate
schema-2 **published selection**. It contains the canonical records and
disjoint admitted additions, with bilingual descriptions, exclusions and
per-source provenance. Publication counts describe this selection. The source
checkpoints' original success/failure/pending and integrity counts remain
separate; unselected captured IDs are never relabeled as unattempted.

`/source-browser.json` then uses schema 2 and binds to the exact
`source-published.json` bytes. Old schema-1 browser data continues to bind only
to `source-index.json`. Publication time is labeled as publication time, not as
a newly completed scan. The underlying capture timestamps remain on every row.

The curated catalog, papers, `data-manifest.json`, and curated machine-data
bundle remain separate. Automatic records are not added to those packages.
There is no new homepage ZIP action; cloning the catalog remains the primary
agent/data entry point.

## 简体中文

此层只从已审阅的**公开**工作流证据中选取原样的已验证采集对象，不伪造新扫描，
不改写原始累计数量，也不把自动发现包装成人工推荐。初始 500 个候选中，495 条非空
描述需要完整英中覆盖，5 条空描述保持为空；翻译完成不等于发布准入。26 条与现有可浏览基线相同的
README 保留采集和译文，但不重复展示。准入后合计为 3,500 条记录、190 条排除和
3,310 条可浏览记录。补充批次的范围决定只能作用于新 ID，不能重新分类基线条目。

原有 3,000 条规范扫描和原有语言文件不变。完成审阅后，新条目进入独立的
`source-published.json` 发布选集；原始失败记录、采集总数和完整来源证据仍单独保留。
界面显示“选集发布”日期，不宣称重新完成了一次扫描。私密的大规模采集 checkpoint
不是此发布流程的输入。

from pathlib import Path
import streamlit as st
from app.charts import POPULATION_LABELS
from app.data import sample_exists


def load_styles(path: Path):
    st.html(f"<style>{path.read_text()}</style>")


def render_header(active):
    pages = {
        "Overview": "/",
        "Response Analysis": "?page=response",
        "Cohort Explorer": "?page=cohort",
    }
    navigation = "".join(
        f"""
        <a
            href="{href}"
            target="_self"
            class="{"active" if label == active else ""}"
        >
            {label}
        </a>
        """
        for label, href in pages.items()
    )
    st.html(
        f"""
        <div class="topbar">
            <div class="brand">
                <span class="brand-name">Loblaw Bio</span>
                <span class="brand-divider"></span>
                <span class="product-name">Immune Response Explorer</span>
            </div>

            <nav class="nav">
                {navigation}
            </nav>
        </div>
        """
    )


def render_hero():
    st.html(
        """
        <div class="hero">
            <div>
                <div class="eyebrow">Overview · Immune profiling</div>
                <div class="hero-title">
                    Mapping the<br>
                    immune landscape.
                </div>
                <div class="hero-copy">
                    This dataset follows immune cell populations measured across biological samples from patients with melanoma and other
                    conditions. Each sample captures five major immune populations: B cells, CD4 T cells, CD8 T cells, NK cells, and monocytes.
                    <br><br>
                    Relative frequencies allow us to compare immune composition across samples and investigate how that composition relates
                    to treatment response.
                </div>
            </div>
            <div class="motif">
                <div class="orbit orbit-one"></div>
                <div class="orbit orbit-two"></div>
                <div class="orbit orbit-three"></div>
                <div class="cell cell-a"></div>
                <div class="cell cell-b"></div>
                <div class="cell cell-c"></div>
                <div class="cell cell-d"></div>
                <div class="cell cell-e"></div>
                <div class="motif-note">
                    5 populations<br>
                    B · CD4 T · CD8 T<br>
                    NK · Monocytes
                </div>
            </div>
        </div>
        """
    )


def render_section_intro(number, label, title, description):
    st.html(
        f"""
        <div class="section-intro">
            <div>
                <div class="section-number">
                    {number} / {label.upper()}
                </div>
                <div class="section-title">
                    {title}
                </div>
            </div>
            <div class="section-copy">
                {description}
            </div>
        </div>
        """
    )


def sample_search():
    sample_id = st.text_input(
        "Find a biological sample",
        value="sample00000",
        placeholder="e.g. sample00000",
    ).strip()
    if not sample_id:
        st.info("Enter a sample ID to inspect its immune composition.")
        st.stop()
    if not sample_exists(sample_id):
        st.warning(f'No sample found for "{sample_id}".')
        st.stop()

    return sample_id


def render_sample_context(sample, composition):
    metadata = sample.iloc[0]
    total_count = int(composition["total_count"].iloc[0])
    st.html(
        f"""
        <div class="sample-context">
            <span>{metadata["sample_id"]}</span>
            <span>{metadata["condition"]}</span>
            <span>{metadata["sample_type"]}</span>
            <span>Day {metadata["day"]}</span>
            <span>{total_count:,} total cells</span>
        </div>
        """
    )


def render_composition_table(composition):
    rows = []
    for _, row in composition.iterrows():
        population = POPULATION_LABELS[row["population"]]
        rows.append(
            f"""
            <tr>
                <td>{row["sample"]}</td>
                <td>{int(row["total_count"]):,}</td>
                <td>{population}</td>
                <td>{int(row["count"]):,}</td>
                <td>{row["percentage"]:.2f}%</td>
            </tr>
            """
        )

    st.html(
        f"""
        <div class="data-table-wrap">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Sample</th>
                        <th>Total count</th>
                        <th>Population</th>
                        <th>Count</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </div>
        """
    )


def render_response_finding(results):
    significant = results[results["significant"]]
    if significant.empty:
        st.html(
            """
            <div class="finding">
                <div class="finding-label">Baseline finding</div>
                <div class="finding-text">
                    No measured immune population significantly distinguished miraclib responders from nonresponders at baseline after
                    multiple-testing correction.
                </div>
                <div class="finding-note">
                    Effect sizes were small across all five populations.
                </div>
            </div>
            """
        )


def render_statistics_table(results):
    rows = []
    for _, row in results.iterrows():
        population = POPULATION_LABELS[row["population"]]
        rows.append(
            f"""
            <tr>
                <td>{population}</td>
                <td>{row["responder_mean"]:.2f}%</td>
                <td>{row["nonresponder_mean"]:.2f}%</td>
                <td>{row["difference"]:+.2f}</td>
                <td>{row["effect_size"]:+.2f}</td>
                <td>{row["p_value"]:.3f}</td>
                <td>{row["adjusted_p_value"]:.3f}</td>
            </tr>
            """
        )

    st.html(
        f"""
        <div class="data-table-wrap">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Population</th>
                        <th>Responder mean</th>
                        <th>Nonresponder mean</th>
                        <th>Difference</th>
                        <th>Cohen's d</th>
                        <th>p-value</th>
                        <th>FDR p-value</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </div>
        """
    )


def render_effect_size_explainer():
    with st.expander("Why report Cohen's d?"):
        st.markdown(
            """
            **Statistical significance tells us whether a difference is supported by the data. Effect size tells us how large that difference actually is.**

            Cohen's d expresses the responder–nonresponder difference relative to the variability between patients. A value near zero
            means the two groups overlap heavily while larger absolute values indicate greater separation.

            For example, baseline B-cell frequency differs by about **0.31 percentage points**, but **Cohen's d ≈ 0.10**. That means
            the difference is small relative to the variation among patients.

            We report both because a statistically detectable difference is not necessarily a useful predictive difference.
            """
        )


def render_subsection(label, title, description):
    st.html(
        f"""
        <div class="subsection">
            <div class="subsection-label">{label}</div>
            <div>
                <div class="subsection-title">{title}</div>
                <div class="subsection-copy">{description}</div>
            </div>
        </div>
        """
    )


def render_longitudinal_table(results):
    rows = []
    for _, row in results.iterrows():
        population = POPULATION_LABELS[row["population"]]
        rows.append(
            f"""
            <tr>
                <td>{population}</td>
                <td>Day {int(row["day"])}</td>
                <td>{row["responder_change"]:+.2f} pp</td>
                <td>{row["nonresponder_change"]:+.2f} pp</td>
                <td>{row["difference"]:+.2f} pp</td>
                <td>{row["effect_size"]:+.2f}</td>
                <td>{row["p_value"]:.3f}</td>
                <td>{row["adjusted_p_value"]:.3f}</td>
            </tr>
            """
        )

    st.html(
        f"""
        <div class="data-table-wrap">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Population</th>
                        <th>Timepoint</th>
                        <th>Responder Δ</th>
                        <th>Nonresponder Δ</th>
                        <th>Difference</th>
                        <th>Cohen's d</th>
                        <th>p-value</th>
                        <th>FDR p-value</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </div>
        """
    )


def render_longitudinal_finding():
    st.html(
        """
        <div class="finding">
            <div class="finding-label">Longitudinal finding</div>
            <div class="finding-text">
                Changes from baseline did not significantly differ between responders and nonresponders after multiple-testing correction.
            </div>
            <div class="finding-note">
                B-cell frequency at Day 14 showed the strongest exploratory signal (p = 0.017), but it did not remain significant after
                FDR correction (adjusted p = 0.168).
            </div>
        </div>
        """
    )


def render_cohort_definition(sample_count):
    st.html(
        f"""
        <div class="cohort-definition">
            <div class="cohort-definition-label">
                Baseline cohort
            </div>
            <div class="cohort-criteria">
                <div>
                    <span>Condition</span>
                    <strong>Melanoma</strong>
                </div>
                <div>
                    <span>Sample type</span>
                    <strong>PBMC</strong>
                </div>
                <div>
                    <span>Treatment</span>
                    <strong>Miraclib</strong>
                </div>
                <div>
                    <span>Timepoint</span>
                    <strong>Day 0</strong>
                </div>
            </div>
            <div class="cohort-result">
                <strong>{sample_count:,}</strong>
                <span>matching samples</span>
            </div>
        </div>
        """
    )


def render_cohort_insight(average):
    st.html(
        f"""
        <div class="cohort-insight">
            <div class="cohort-insight-label">
                Cohort insight
            </div>
            <div class="cohort-insight-text">
                Male melanoma responders averaged
                <strong>{average:,.2f} B cells</strong>
                at baseline across all treatments and sample types.
            </div>
        </div>
        """
    )

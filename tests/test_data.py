import sqlite3
import pytest
from load_data import DB_PATH


@pytest.fixture
def connection():
    with sqlite3.connect(DB_PATH) as db:
        yield db


def test_database_record_counts(connection):
    expected = {
        "subjects": 3500,
        "samples": 10500,
        "cell_counts": 52500,
    }

    for table, count in expected.items():
        actual = connection.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]
        assert actual == count


def test_every_sample_has_five_populations(connection):
    counts = connection.execute(
        """
        SELECT COUNT(*)
        FROM cell_counts
        GROUP BY sample_id
        """
    ).fetchall()
    assert len(counts) == 10500
    assert all(count == 5 for (count,) in counts)


def test_sample_frequencies_sum_to_100(connection):
    totals = connection.execute(
        """
        SELECT SUM(percentage)
        FROM sample_frequencies
        GROUP BY sample
        """
    ).fetchall()
    assert len(totals) == 10500
    for (total,) in totals:
        assert total == pytest.approx(100.0)


def test_known_sample_frequency(connection):
    result = connection.execute(
        """
        SELECT total_count, count, percentage
        FROM sample_frequencies
        WHERE sample = 'sample00000'
          AND population = 'b_cell'
        """
    ).fetchone()
    total_count, count, percentage = result
    assert total_count == 93214
    assert count == 10908
    assert percentage == pytest.approx(100 * 10908 / 93214)

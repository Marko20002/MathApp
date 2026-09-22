import csv
import pytest
from mathapp_ml.data import COLUMNS, load_csv, effective_groups, question_hash
from mathapp_ml.training import split_examples, train


def write_csv(path, records):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(records)
    return path


def example(id='calc_1', **changes):
    return dict(id=id, question='Find the derivative of sin(x).', label='CALCULUS',
                subtopic='derivatives', language='en', source='synthetic',
                group_id=id, review_status='pending') | changes


def test_csv_preserves_quoted_commas_and_unicode(tmp_path):
    rows, report = load_csv(write_csv(tmp_path / 'data.csv', [example(question='For x→0, evaluate sin(x)/x.')]))
    assert rows[0]['question'] == 'For x→0, evaluate sin(x)/x.'
    assert report['rows'] == 1


@pytest.mark.parametrize('changes', [{'label': 'nan'}, {'question': ' '}, {'language': 'xx'}, {'review_status': 'done'}])
def test_invalid_data_fails_without_printing_question(tmp_path, changes):
    with pytest.raises(ValueError):
        load_csv(write_csv(tmp_path / 'data.csv', [example(**changes)]))


def test_duplicate_normalized_question_rejected(tmp_path):
    with pytest.raises(ValueError, match='duplicate normalized question'):
        load_csv(write_csv(tmp_path / 'data.csv', [example(), example('calc_2', question=' Find  the derivative of sin(x). ')]))


def test_transitive_template_groups():
    rows = [example('a', question='lim x->2 x^2'), example('b', question='lim x->3 x^3'),
            example('c', question='Some different task', group_id='b')]
    assert len(set(effective_groups(rows))) == 1


def test_hash_preserves_math_superscripts():
    assert question_hash('Find x²') != question_hash('Find x2')
    assert question_hash('Find X') != question_hash('Find x')


def test_group_splits_are_disjoint():
    rows = []
    for label in ['CALCULUS', 'PROBABILITY', 'DISCRETE']:
        for i in range(20):
            for suffix in ['a', 'b']:
                rows.append(example(f'{label}_{i}{suffix}', label=label,
                    question=f'{label} task {chr(65+i)} variant {suffix}', group_id=f'{label}_{i}'))
    splits, groups = split_examples(rows)
    memberships = [set(groups[i] for i in split) for split in splits.values()]
    assert not memberships[0] & memberships[1]
    assert not memberships[0] & memberships[2]
    assert not memberships[1] & memberships[2]
    assert sum(len(v) for v in splits.values()) == len(rows)


def test_pending_data_requires_explicit_opt_in(tmp_path):
    path = write_csv(tmp_path / 'data.csv', [example()])
    with pytest.raises(ValueError, match='No approved'):
        train(path, tmp_path / 'candidate')
